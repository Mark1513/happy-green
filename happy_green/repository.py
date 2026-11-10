"""Adaptador PostgreSQL. Uma conexão por operação, fechada ao sair do contexto."""

import logging
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Iterator
from uuid import UUID

import psycopg
from psycopg import sql
from psycopg.rows import dict_row

from .domain import Categoria, ContaFinanceira, Despesa, OrcamentoMensal, Receita, TipoLancamento
from .errors import (ConfigurationError, ConflictError, NotFoundError,
                     PersistenceError, ValidationError)
from .ports import Carteira, RepositorioFinanceiro

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DatabaseConfig:
    host: str
    port: int
    dbname: str
    user: str
    password: str = field(repr=False)

    @contextmanager
    def conectar(self) -> Iterator[psycopg.Connection]:
        try:
            with psycopg.connect(
                host=self.host, port=self.port, dbname=self.dbname,
                user=self.user, password=self.password,
                sslmode="require", connect_timeout=10,
                application_name="happy-green", row_factory=dict_row,
                options="-c statement_timeout=15000 -c timezone=America/Sao_Paulo",
            ) as conn:
                yield conn
        except psycopg.errors.UniqueViolation:
            raise ConflictError("Já existe um registro com esse nome ou identificação.") from None
        except psycopg.errors.ForeignKeyViolation:
            raise ConflictError(
                "A operação conflita com registros vinculados. Atualize os dados e confira as referências."
            ) from None
        except (psycopg.errors.CheckViolation, psycopg.errors.NumericValueOutOfRange,
                psycopg.errors.StringDataRightTruncation):
            raise ValidationError("Os dados não atendem às regras do banco. Confira os valores.") from None
        except (psycopg.errors.UndefinedTable, psycopg.errors.InvalidSchemaName):
            raise ConfigurationError("A estrutura do banco ainda não foi criada. Aplique a migração 001.") from None
        except psycopg.Error as exc:
            # Não registrar URL, senha ou parâmetros financeiros.
            logger.error("Falha PostgreSQL: %s", type(exc).__name__)
            raise PersistenceError(
                "Não foi possível concluir a operação no Supabase. Confira a conexão e tente novamente."
            ) from None


class RepositorioPostgres(RepositorioFinanceiro):
    def __init__(self, config: DatabaseConfig):
        self._config = config

    def carregar(self) -> Carteira:
        with self._config.conectar() as conn:
            conn.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
            contas = {row["id"]: ContaFinanceira(row["nome"], row["saldo_inicial"], row["id"])
                      for row in conn.execute("SELECT * FROM happy_green.contas ORDER BY lower(nome)")}
            categorias = {row["id"]: Categoria(row["nome"], row["tipo"], row["id"])
                          for row in conn.execute("SELECT * FROM happy_green.categorias ORDER BY tipo,lower(nome)")}
            tipos = {"RECEITA": Receita, "DESPESA": Despesa}
            lancamentos = tuple(
                tipos[row["tipo"]](contas[row["conta_id"]], categorias[row["categoria_id"]],
                                   row["descricao"], row["valor"], row["data"], row["id"])
                for row in conn.execute("SELECT * FROM happy_green.lancamentos ORDER BY data DESC,created_at DESC,id")
            )
            orcamentos = tuple(
                OrcamentoMensal(categorias[row["categoria_id"]], row["mes"], row["limite"], row["id"])
                for row in conn.execute("SELECT * FROM happy_green.orcamentos ORDER BY mes DESC,categoria_id")
            )
            return Carteira(tuple(contas.values()), tuple(categorias.values()), lancamentos, orcamentos)

    @staticmethod
    def _gravar_conta(conn, conta, atualizar=False):
        if atualizar:
            result = conn.execute("UPDATE happy_green.contas SET nome=%s,saldo_inicial=%s WHERE id=%s",
                                  (conta.nome, conta.saldo_inicial, conta.id))
            if not result.rowcount:
                raise NotFoundError("Conta removida por outra sessão. Atualize os dados.")
        else:
            conn.execute("INSERT INTO happy_green.contas(id,nome,saldo_inicial) VALUES (%s,%s,%s)",
                         (conta.id, conta.nome, conta.saldo_inicial))

    @staticmethod
    def _gravar_categoria(conn, categoria, atualizar=False):
        if atualizar:
            result = conn.execute("UPDATE happy_green.categorias SET nome=%s,tipo=%s WHERE id=%s",
                                  (categoria.nome, categoria.tipo.value, categoria.id))
            if not result.rowcount:
                raise NotFoundError("Categoria removida por outra sessão. Atualize os dados.")
        else:
            conn.execute("INSERT INTO happy_green.categorias(id,nome,tipo) VALUES (%s,%s,%s)",
                         (categoria.id, categoria.nome, categoria.tipo.value))

    @staticmethod
    def _gravar_lancamento(conn, item, atualizar=False):
        valores = (item.conta.id, item.categoria.id, item.tipo.value,
                   item.descricao, item.valor, item.data, item.id)
        if atualizar:
            result = conn.execute("""UPDATE happy_green.lancamentos
                SET conta_id=%s,categoria_id=%s,tipo=%s,descricao=%s,valor=%s,data=%s WHERE id=%s""", valores)
            if not result.rowcount:
                raise NotFoundError("Lançamento removido por outra sessão. Atualize os dados.")
        else:
            conn.execute("""INSERT INTO happy_green.lancamentos
                (conta_id,categoria_id,tipo,descricao,valor,data,id) VALUES (%s,%s,%s,%s,%s,%s,%s)""", valores)

    @staticmethod
    def _gravar_orcamento(conn, item):
        conn.execute("""INSERT INTO happy_green.orcamentos(id,categoria_id,mes,limite)
            VALUES (%s,%s,%s,%s) ON CONFLICT (categoria_id,mes)
            DO UPDATE SET limite=EXCLUDED.limite""", (item.id, item.categoria.id, item.mes, item.limite))

    def salvar_conta(self, conta, *, atualizar=False):
        with self._config.conectar() as conn:
            self._gravar_conta(conn, conta, atualizar)

    def salvar_categoria(self, categoria, *, atualizar=False):
        with self._config.conectar() as conn:
            self._gravar_categoria(conn, categoria, atualizar)

    def salvar_lancamento(self, lancamento, *, atualizar=False):
        with self._config.conectar() as conn:
            self._gravar_lancamento(conn, lancamento, atualizar)

    def salvar_orcamento(self, orcamento):
        with self._config.conectar() as conn:
            self._gravar_orcamento(conn, orcamento)

    def excluir(self, entidade: str, id: UUID):
        if entidade not in {"contas", "categorias", "lancamentos", "orcamentos"}:
            raise ValidationError("Operação inválida.")
        with self._config.conectar() as conn:
            result = conn.execute(sql.SQL("DELETE FROM happy_green.{} WHERE id=%s")
                                  .format(sql.Identifier(entidade)), (id,))
            if not result.rowcount:
                raise NotFoundError("O registro já foi removido. Atualize os dados.")

    def carregar_demonstracao(self, carteira: Carteira):
        with self._config.conectar() as conn:
            # Serializa a carga e bloqueia escritas concorrentes durante a verificação.
            conn.execute("""LOCK TABLE happy_green.contas,happy_green.categorias,
                happy_green.lancamentos,happy_green.orcamentos IN SHARE ROW EXCLUSIVE MODE""")
            ocupado = conn.execute("""SELECT EXISTS (
                SELECT 1 FROM happy_green.contas UNION ALL SELECT 1 FROM happy_green.categorias
                UNION ALL SELECT 1 FROM happy_green.lancamentos UNION ALL SELECT 1 FROM happy_green.orcamentos
            ) AS ocupado""").fetchone()["ocupado"]
            if ocupado:
                raise ConflictError("A demonstração só pode ser carregada em um banco vazio.")
            for conta in carteira.contas:
                self._gravar_conta(conn, conta)
            for categoria in carteira.categorias:
                self._gravar_categoria(conn, categoria)
            for item in carteira.lancamentos:
                self._gravar_lancamento(conn, item)
            for item in carteira.orcamentos:
                self._gravar_orcamento(conn, item)
