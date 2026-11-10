from datetime import date, timedelta
from decimal import Decimal

import pytest

from happy_green.domain import (Categoria, ContaFinanceira, Despesa, Lancamento,
                                OrcamentoMensal, Receita, TipoLancamento, dinheiro)
from happy_green.errors import ValidationError
from happy_green.presentation import brl, ler_brl


def objetos():
    return (ContaFinanceira("Carteira", "0"), Categoria("Salário", TipoLancamento.RECEITA),
            Categoria("Comida", TipoLancamento.DESPESA))


@pytest.mark.parametrize("valor", [0.1, True, "NaN", "Infinity", "-Infinity", "abc", "1000000000000", None])
def test_rejeita_dinheiro_invalido(valor):
    with pytest.raises(ValidationError):
        dinheiro(valor)


def test_arredondamento_exato_e_formato_brl():
    assert dinheiro("1.005") == Decimal("1.01")
    assert dinheiro("-1.005") == Decimal("-1.01")
    assert dinheiro("0.10") + dinheiro("0.20") == Decimal("0.30")
    assert brl(Decimal("1234.56")) == "R$ 1.234,56"
    assert brl(Decimal("-0.01")) == "R$ -0,01"


@pytest.mark.parametrize("valor,esperado", [("1.500,00", "1500.00"), ("1500,00", "1500.00"),
    ("1500.00", "1500.00"), ("R$ 12,50", "12.50"), ("-100,00", "-100.00"), ("5", "5.00")])
def test_parse_monetario_sem_float(valor, esperado):
    assert ler_brl(valor) == Decimal(esperado)


@pytest.mark.parametrize("valor", ["", "1.50,00", "1,234", "1.500", "1e3", "nan", "--1", "1,2,3"])
def test_rejeita_formato_ambiguo(valor):
    with pytest.raises(ValidationError):
        ler_brl(valor)


def test_classe_abstrata_e_polimorfismo():
    conta, renda, gasto = objetos()
    with pytest.raises(TypeError):
        Lancamento(conta, renda, "Exemplo", "10", date.today())
    itens = [Receita(conta, renda, "Bolsa", "1500", date.today()),
             Despesa(conta, gasto, "Comida", "300", date.today())]
    assert [x.calcular_impacto_no_saldo() for x in itens] == [Decimal("1500"), Decimal("-300")]
    assert conta.calcular_saldo(itens) == Decimal("1200.00")


def test_encapsulamento_impede_setter_que_burla_validacao():
    conta = ContaFinanceira("Carteira")
    with pytest.raises(AttributeError):
        conta.saldo_inicial = Decimal("999")


@pytest.mark.parametrize("valor", ["0", "-1", "0.001"])
def test_lancamentos_exigem_valor_positivo(valor):
    conta, _, gasto = objetos()
    with pytest.raises(ValidationError):
        Despesa(conta, gasto, "Compra", valor, date.today())


def test_categoria_data_e_descricao_protegidas():
    conta, renda, gasto = objetos()
    with pytest.raises(ValidationError):
        Despesa(conta, renda, "Compra", "10", date.today())
    with pytest.raises(ValidationError):
        Receita(conta, renda, " ", "10", date.today())
    with pytest.raises(ValidationError):
        Despesa(conta, gasto, "Amanhã", "10", date.today() + timedelta(days=1))
    with pytest.raises(ValidationError):
        Categoria("", TipoLancamento.DESPESA)
    with pytest.raises(ValidationError):
        Categoria("Teste", "OUTRO")


def test_saldo_respeita_conta_e_inclui_inicial():
    conta, renda, gasto = objetos()
    outra = ContaFinanceira("Banco", "100")
    itens = [Receita(conta, renda, "Bolsa", "1500", date.today()),
             Despesa(outra, gasto, "Compra", "40", date.today())]
    assert conta.calcular_saldo(itens) == Decimal("1500")
    assert outra.calcular_saldo(itens) == Decimal("60")


def test_orcamento_mes_categoria_e_limite():
    conta, renda, gasto = objetos()
    hoje = date.today()
    anterior = hoje.replace(day=1) - timedelta(days=1)
    item = OrcamentoMensal(gasto, hoje, "250")
    itens = [Despesa(conta, gasto, "Agora", "300", hoje),
             Despesa(conta, gasto, "Antes", "100", anterior)]
    assert item.mes.day == 1
    assert item.calcular_consumo(itens) == Decimal("300")
    assert item.limite_ultrapassado(itens)
    with pytest.raises(ValidationError):
        OrcamentoMensal(renda, hoje, "250")
    with pytest.raises(ValidationError):
        OrcamentoMensal(gasto, hoje, "0")
