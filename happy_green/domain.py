"""Regras financeiras puras: não importa Streamlit nem acessa o banco."""

from abc import ABC, abstractmethod
from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from enum import StrEnum
from typing import Iterable
from uuid import UUID, uuid4

from .clock import hoje
from .errors import ValidationError

CENTAVO = Decimal("0.01")
ZERO = Decimal("0.00")
MAX_MONEY = Decimal("999999999999.99")  # NUMERIC(14, 2)


def dinheiro(valor: Decimal | str | int) -> Decimal:
    """Aceita valores exatos; a interface faz a tradução da notação brasileira."""
    if isinstance(valor, (float, bool)):
        raise ValidationError("Informe dinheiro como texto, inteiro ou Decimal; float não é aceito.")
    try:
        numero = Decimal(valor)
        if not numero.is_finite() or abs(numero) > MAX_MONEY:
            raise ValueError
        return numero.quantize(CENTAVO, rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError, TypeError):
        raise ValidationError("Informe um valor monetário válido dentro do limite permitido.") from None


def texto(valor: str, campo: str, limite: int = 80) -> str:
    if not isinstance(valor, str) or not valor.strip():
        raise ValidationError(f"{campo} é obrigatório.")
    valor = valor.strip()
    if len(valor) > limite:
        raise ValidationError(f"{campo} deve ter até {limite} caracteres.")
    return valor


def data_valida(valor: date) -> date:
    if not isinstance(valor, date) or isinstance(valor, datetime):
        raise ValidationError("Informe uma data válida.")
    if not date(1900, 1, 1) <= valor <= date(2100, 12, 31):
        raise ValidationError("A data deve estar entre 1900 e 2100.")
    return valor


def identificador(valor: UUID | None = None) -> UUID:
    if valor is not None and not isinstance(valor, UUID):
        raise ValidationError("Identificador inválido.")
    return valor or uuid4()


class TipoLancamento(StrEnum):
    RECEITA = "RECEITA"
    DESPESA = "DESPESA"


class Entidade:
    def __init__(self, id: UUID | None = None):
        self._id = identificador(id)

    @property
    def id(self) -> UUID:
        return self._id


class ContaFinanceira(Entidade):
    def __init__(self, nome: str, saldo_inicial=ZERO, id: UUID | None = None):
        super().__init__(id)
        self._nome = texto(nome, "Nome da conta")
        self._saldo_inicial = dinheiro(saldo_inicial)

    @property
    def nome(self) -> str:
        return self._nome

    @property
    def saldo_inicial(self) -> Decimal:
        return self._saldo_inicial

    def calcular_saldo(self, lancamentos: Iterable["Lancamento"]) -> Decimal:
        return self.saldo_inicial + sum(
            (item.calcular_impacto_no_saldo() for item in lancamentos if item.conta.id == self.id),
            ZERO,
        )


class Categoria(Entidade):
    def __init__(self, nome: str, tipo: TipoLancamento, id: UUID | None = None):
        super().__init__(id)
        self._nome = texto(nome, "Nome da categoria")
        try:
            self._tipo = TipoLancamento(tipo)
        except (ValueError, TypeError):
            raise ValidationError("Tipo da categoria inválido.") from None

    @property
    def nome(self) -> str:
        return self._nome

    @property
    def tipo(self) -> TipoLancamento:
        return self._tipo


class Lancamento(Entidade, ABC):
    def __init__(self, conta: ContaFinanceira, categoria: Categoria, descricao: str,
                 valor: Decimal | str | int, data: date, id: UUID | None = None):
        super().__init__(id)
        if not isinstance(conta, ContaFinanceira) or not isinstance(categoria, Categoria):
            raise ValidationError("Selecione uma conta e uma categoria válidas.")
        if categoria.tipo != self.tipo:
            raise ValidationError("A categoria não corresponde ao tipo do lançamento.")
        self._conta = conta
        self._categoria = categoria
        self._descricao = texto(descricao, "Descrição", 160)
        self._valor = dinheiro(valor)
        if self._valor <= ZERO:
            raise ValidationError("O valor do lançamento deve ser maior que zero.")
        self._data = data_valida(data)
        if self._data > hoje():
            raise ValidationError("Registre apenas movimentações realizadas, com data até hoje.")

    @property
    def conta(self) -> ContaFinanceira:
        return self._conta

    @property
    def categoria(self) -> Categoria:
        return self._categoria

    @property
    def descricao(self) -> str:
        return self._descricao

    @property
    def valor(self) -> Decimal:
        return self._valor

    @property
    def data(self) -> date:
        return self._data

    @property
    @abstractmethod
    def tipo(self) -> TipoLancamento:
        """Discriminador usado na persistência, sem substituir o polimorfismo."""

    @abstractmethod
    def calcular_impacto_no_saldo(self) -> Decimal:
        """Comportamento chamado pelo cálculo do saldo e dos resultados."""


class Receita(Lancamento):
    @property
    def tipo(self) -> TipoLancamento:
        return TipoLancamento.RECEITA

    def calcular_impacto_no_saldo(self) -> Decimal:
        return self.valor


class Despesa(Lancamento):
    @property
    def tipo(self) -> TipoLancamento:
        return TipoLancamento.DESPESA

    def calcular_impacto_no_saldo(self) -> Decimal:
        return -self.valor


class OrcamentoMensal(Entidade):
    def __init__(self, categoria: Categoria, mes: date, limite, id: UUID | None = None):
        super().__init__(id)
        if not isinstance(categoria, Categoria) or categoria.tipo != TipoLancamento.DESPESA:
            raise ValidationError("Orçamentos exigem uma categoria de despesa.")
        self._categoria = categoria
        self._mes = data_valida(mes).replace(day=1)
        self._limite = dinheiro(limite)
        if self._limite <= ZERO:
            raise ValidationError("O limite do orçamento deve ser maior que zero.")

    @property
    def categoria(self) -> Categoria:
        return self._categoria

    @property
    def mes(self) -> date:
        return self._mes

    @property
    def limite(self) -> Decimal:
        return self._limite

    def calcular_consumo(self, lancamentos: Iterable[Lancamento]) -> Decimal:
        return sum((item.valor for item in lancamentos
                    if item.categoria.id == self.categoria.id
                    and item.data.replace(day=1) == self.mes), ZERO)

    def limite_ultrapassado(self, lancamentos: Iterable[Lancamento]) -> bool:
        return self.calcular_consumo(lancamentos) > self.limite
