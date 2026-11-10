"""Casos de uso: a interface não precisa conhecer SQL."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from .domain import (ZERO, Categoria, ContaFinanceira, Despesa, Lancamento,
                     OrcamentoMensal, Receita, TipoLancamento)
from .errors import ConflictError, NotFoundError, ValidationError
from .ports import Carteira, RepositorioFinanceiro


@dataclass(frozen=True)
class ResumoMensal:
    saldo_total: Decimal
    receitas: Decimal
    despesas: Decimal
    resultado: Decimal


def buscar(itens, id: UUID, nome: str):
    encontrado = next((item for item in itens if item.id == id), None)
    if encontrado is None:
        raise NotFoundError(f"{nome} não encontrado. Atualize a página e tente novamente.")
    return encontrado


class ServicoFinanceiro:
    def __init__(self, repositorio: RepositorioFinanceiro):
        self._repositorio = repositorio

    def carregar(self) -> Carteira:
        return self._repositorio.carregar()

    def salvar_conta(self, nome: str, saldo_inicial, id: UUID | None = None):
        if id:
            buscar(self.carregar().contas, id, "Conta")
        conta = ContaFinanceira(nome, saldo_inicial, id)
        self._repositorio.salvar_conta(conta, atualizar=id is not None)
        return conta

    def salvar_categoria(self, nome: str, tipo: TipoLancamento, id: UUID | None = None):
        if id:
            buscar(self.carregar().categorias, id, "Categoria")
        categoria = Categoria(nome, tipo, id)
        self._repositorio.salvar_categoria(categoria, atualizar=id is not None)
        return categoria

    def salvar_lancamento(self, conta_id: UUID, categoria_id: UUID, tipo: TipoLancamento,
                         descricao: str, valor, data: date, id: UUID | None = None):
        carteira = self.carregar()
        if id:
            buscar(carteira.lancamentos, id, "Lançamento")
        conta = buscar(carteira.contas, conta_id, "Conta")
        categoria = buscar(carteira.categorias, categoria_id, "Categoria")
        # A seleção do construtor é feita uma vez; os cálculos usam o método abstrato.
        construtor = {TipoLancamento.RECEITA: Receita, TipoLancamento.DESPESA: Despesa}.get(tipo)
        if construtor is None:
            raise ValidationError("Tipo de lançamento inválido.")
        lancamento = construtor(conta, categoria, descricao, valor, data, id)
        self._repositorio.salvar_lancamento(lancamento, atualizar=id is not None)
        return lancamento

    def salvar_orcamento(self, categoria_id: UUID, mes: date, limite):
        carteira = self.carregar()
        categoria = buscar(carteira.categorias, categoria_id, "Categoria")
        mes = mes.replace(day=1)
        existente = next((item for item in carteira.orcamentos
                          if item.categoria.id == categoria_id and item.mes == mes), None)
        orcamento = OrcamentoMensal(categoria, mes, limite, existente.id if existente else None)
        self._repositorio.salvar_orcamento(orcamento)
        return orcamento

    def excluir(self, entidade: str, id: UUID):
        carteira = self.carregar()
        colecoes = {"contas": carteira.contas, "categorias": carteira.categorias,
                    "lancamentos": carteira.lancamentos, "orcamentos": carteira.orcamentos}
        if entidade not in colecoes:
            raise ValidationError("Operação inválida.")
        buscar(colecoes[entidade], id, "Registro")
        if entidade == "contas" and any(item.conta.id == id for item in carteira.lancamentos):
            raise ConflictError("Esta conta possui lançamentos e não pode ser excluída.")
        if entidade == "categorias" and (
            any(item.categoria.id == id for item in carteira.lancamentos)
            or any(item.categoria.id == id for item in carteira.orcamentos)
        ):
            raise ConflictError("Esta categoria possui lançamentos ou orçamentos e não pode ser excluída.")
        self._repositorio.excluir(entidade, id)

    @staticmethod
    def filtrar(carteira: Carteira, inicio: date, fim: date, conta_id=None,
                categoria_id=None, tipo=None) -> tuple[Lancamento, ...]:
        if inicio > fim:
            raise ValidationError("A data inicial deve ser anterior ou igual à final.")
        return tuple(item for item in carteira.lancamentos
                     if inicio <= item.data <= fim
                     and (conta_id is None or item.conta.id == conta_id)
                     and (categoria_id is None or item.categoria.id == categoria_id)
                     and (tipo is None or item.tipo == tipo))

    @staticmethod
    def resumir(carteira: Carteira, mes: date) -> ResumoMensal:
        mensal = [item for item in carteira.lancamentos
                  if item.data.replace(day=1) == mes.replace(day=1)]
        impactos = [item.calcular_impacto_no_saldo() for item in mensal]
        return ResumoMensal(
            saldo_total=sum((conta.calcular_saldo(carteira.lancamentos)
                             for conta in carteira.contas), ZERO),
            receitas=sum((valor for valor in impactos if valor > ZERO), ZERO),
            despesas=-sum((valor for valor in impactos if valor < ZERO), ZERO),
            resultado=sum(impactos, ZERO),
        )

    def carregar_demonstracao(self):
        from .demo import criar_demonstracao
        self._repositorio.carregar_demonstracao(criar_demonstracao())
