"""Carga explícita. Nenhuma escrita acontece durante import ou rerun."""

from datetime import date

from .clock import hoje as data_atual
from .domain import Categoria, ContaFinanceira, Despesa, OrcamentoMensal, Receita, TipoLancamento
from .ports import Carteira


def criar_demonstracao() -> Carteira:
    hoje = data_atual()
    conta = ContaFinanceira("Minha carteira", "0.00")
    renda = Categoria("Bolsa e salário", TipoLancamento.RECEITA)
    comida = Categoria("Alimentação", TipoLancamento.DESPESA)
    transporte = Categoria("Transporte", TipoLancamento.DESPESA)
    lazer = Categoria("Lazer", TipoLancamento.DESPESA)
    lancamentos = (
        Receita(conta, renda, "Bolsa de estudos", "1500.00", hoje),
        Despesa(conta, comida, "Compras do mês", "300.00", hoje),
        Despesa(conta, transporte, "Passe de transporte", "120.00", hoje),
    )
    return Carteira((conta,), (renda, comida, transporte, lazer), lancamentos,
                    (OrcamentoMensal(comida, hoje, "250.00"),))
