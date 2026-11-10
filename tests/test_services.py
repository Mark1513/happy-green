from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest

from happy_green.clock import hoje as data_atual
from happy_green.domain import TipoLancamento as Tipo
from happy_green.errors import ConflictError, NotFoundError, ValidationError


def test_cenario_completo_de_demonstracao(service):
    service.carregar_demonstracao()
    carteira = service.carregar()
    hoje = data_atual()
    resumo = service.resumir(carteira, hoje)
    assert resumo.saldo_total == Decimal("1080.00")
    assert resumo.receitas == Decimal("1500.00")
    assert resumo.despesas == Decimal("420.00")
    assert resumo.resultado == Decimal("1080.00")
    assert carteira.orcamentos[0].limite_ultrapassado(carteira.lancamentos)
    transporte = next(x for x in carteira.lancamentos if x.categoria.nome == "Transporte")
    service.salvar_lancamento(transporte.conta.id, transporte.categoria.id, Tipo.DESPESA,
                             transporte.descricao, "150", transporte.data, transporte.id)
    assert service.resumir(service.carregar(), hoje).saldo_total == Decimal("1050.00")
    comida = next(x for x in carteira.lancamentos if x.categoria.nome == "Alimentação")
    service.excluir("lancamentos", comida.id)
    carteira = service.carregar()
    assert service.resumir(carteira, hoje).saldo_total == Decimal("1350.00")
    assert not carteira.orcamentos[0].limite_ultrapassado(carteira.lancamentos)


def test_resultado_mensal_diferente_de_saldo_acumulado(service):
    hoje = data_atual()
    antes = hoje.replace(day=1) - timedelta(days=1)
    conta = service.salvar_conta("Banco", "100")
    cat = service.salvar_categoria("Renda", Tipo.RECEITA)
    service.salvar_lancamento(conta.id, cat.id, Tipo.RECEITA, "Anterior", "500", antes)
    service.salvar_lancamento(conta.id, cat.id, Tipo.RECEITA, "Atual", "200", hoje)
    resumo = service.resumir(service.carregar(), hoje)
    assert resumo.saldo_total == Decimal("800")
    assert resumo.resultado == Decimal("200")


def test_referencias_e_duplicatas(service):
    service.carregar_demonstracao()
    carteira = service.carregar()
    with pytest.raises(ConflictError):
        service.excluir("contas", carteira.contas[0].id)
    with pytest.raises(ConflictError):
        service.excluir("categorias", carteira.orcamentos[0].categoria.id)
    with pytest.raises(ConflictError):
        service.salvar_conta(" MINHA CARTEIRA ", "0")
    with pytest.raises(ConflictError):
        service.carregar_demonstracao()
    with pytest.raises(NotFoundError):
        service.salvar_conta("Fantasma", "0", uuid4())


def test_orcamento_unico_atualiza_e_categoria_vinculada(service):
    categoria = service.salvar_categoria("Comida", Tipo.DESPESA)
    original = service.salvar_orcamento(categoria.id, data_atual(), "250")
    atualizado = service.salvar_orcamento(categoria.id, data_atual().replace(day=1), "300")
    assert len(service.carregar().orcamentos) == 1
    assert atualizado.id == original.id
    assert service.carregar().orcamentos[0].limite == Decimal("300")
    with pytest.raises(ConflictError):
        service.salvar_categoria("Comida", Tipo.RECEITA, categoria.id)


def test_edicao_de_conta_e_categoria_reconstroi_associacoes(service):
    service.carregar_demonstracao()
    carteira = service.carregar()
    conta = carteira.contas[0]
    service.salvar_conta("Novo nome", "10", conta.id)
    categoria = carteira.orcamentos[0].categoria
    service.salvar_categoria("Mercado", categoria.tipo, categoria.id)
    nova = service.carregar()
    assert all(x.conta.nome == "Novo nome" for x in nova.lancamentos)
    assert nova.orcamentos[0].categoria.nome == "Mercado"
    assert service.resumir(nova, data_atual()).saldo_total == Decimal("1090")


def test_filtros_combinados_e_periodo_invertido(service):
    service.carregar_demonstracao()
    carteira = service.carregar()
    gasto = next(x for x in carteira.lancamentos if x.categoria.nome == "Transporte")
    itens = service.filtrar(carteira, data_atual(), data_atual(), gasto.conta.id, gasto.categoria.id, Tipo.DESPESA)
    assert len(itens) == 1 and itens[0].id == gasto.id
    with pytest.raises(ValidationError):
        service.filtrar(carteira, data_atual(), data_atual() - timedelta(days=1))


def test_exclusao_de_registros_sem_vinculos(service):
    conta = service.salvar_conta("Vazia", "0")
    service.excluir("contas", conta.id)
    assert not service.carregar().contas
    with pytest.raises(ValidationError):
        service.excluir("tabela_invalida", uuid4())
