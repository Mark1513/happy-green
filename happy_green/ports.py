"""Contrato que permite testar os serviços sem banco nem interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from .domain import Categoria, ContaFinanceira, Lancamento, OrcamentoMensal


@dataclass(frozen=True)
class Carteira:
    contas: tuple[ContaFinanceira, ...] = ()
    categorias: tuple[Categoria, ...] = ()
    lancamentos: tuple[Lancamento, ...] = ()
    orcamentos: tuple[OrcamentoMensal, ...] = ()


class RepositorioFinanceiro(ABC):
    @abstractmethod
    def carregar(self) -> Carteira: ...

    @abstractmethod
    def salvar_conta(self, conta: ContaFinanceira, *, atualizar: bool = False): ...

    @abstractmethod
    def salvar_categoria(self, categoria: Categoria, *, atualizar: bool = False): ...

    @abstractmethod
    def salvar_lancamento(self, lancamento: Lancamento, *, atualizar: bool = False): ...

    @abstractmethod
    def salvar_orcamento(self, orcamento: OrcamentoMensal): ...

    @abstractmethod
    def excluir(self, entidade: str, id: UUID): ...

    @abstractmethod
    def carregar_demonstracao(self, carteira: Carteira): ...
