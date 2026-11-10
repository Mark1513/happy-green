from pathlib import Path
from decimal import Decimal

import pytest
from streamlit.testing.v1 import AppTest

from happy_green import bootstrap
from happy_green.errors import ConfigurationError
from happy_green.clock import hoje

APP = Path(__file__).parents[1] / "streamlit_app.py"


def iniciar(monkeypatch, service, demonstracao=True):
    if demonstracao:
        service.carregar_demonstracao()
    monkeypatch.setattr(bootstrap, "get_service", lambda: service)
    return AppTest.from_file(str(APP), default_timeout=15).run()


@pytest.mark.parametrize("pagina", ["Visão geral", "Lançamentos", "Contas", "Categorias", "Orçamentos", "Resumo mensal", "Sobre o projeto"])
def test_paginas_sem_excecoes(monkeypatch, service, pagina):
    app = iniciar(monkeypatch, service)
    app.sidebar.radio[0].set_value(pagina).run()
    assert not app.exception
    assert not app.error


def test_dashboard_exibe_valores_do_dominio(monkeypatch, service):
    app = iniciar(monkeypatch, service)
    assert [x.value for x in app.metric] == ["R$ 1.080,00", "R$ 1.500,00", "R$ 420,00", "R$ 1.080,00"]
    assert any("Limite ultrapassado" in x.value for x in app.warning)


def test_banco_vazio_e_carga_explicitamente_acionada(monkeypatch, service):
    app = iniciar(monkeypatch, service, demonstracao=False)
    assert not service.carregar().contas
    next(x for x in app.button if x.label == "Carregar demonstração").click().run()
    assert not app.exception
    assert len(service.carregar().lancamentos) == 3
    app.run()
    assert len(service.carregar().lancamentos) == 3


def test_cadastro_pela_interface_e_rerun_sem_duplicar(monkeypatch, service):
    app = iniciar(monkeypatch, service, demonstracao=False)
    app.sidebar.radio[0].set_value("Contas").run()
    app.text_input[0].set_value("Conta UI")
    app.text_input[1].set_value("100,25")
    next(x for x in app.button if x.label == "Salvar conta").click().run()
    assert not app.exception
    assert not app.error
    assert len(service.carregar().contas) == 1
    assert service.carregar().contas[0].nome == "Conta UI"
    app.run()
    assert len(service.carregar().contas) == 1


def test_configuracao_pendente_nao_simula_persistencia(monkeypatch):
    def pendente():
        raise ConfigurationError("Configure a conexão com o Supabase para começar.")
    monkeypatch.setattr(bootstrap, "get_service", pendente)
    app = AppTest.from_file(str(APP), default_timeout=15).run()
    assert not app.exception
    assert any("Configure a conexão" in x.value for x in app.warning)
    assert not app.metric


def test_despesa_criada_pelo_formulario_sem_duplicacao(monkeypatch, service):
    app = iniciar(monkeypatch, service)
    app.sidebar.radio[0].set_value("Lançamentos").run()
    app.text_input[0].set_value("Café de teste")
    app.text_input[1].set_value("10,50")
    next(x for x in app.button if x.label == "Salvar lançamento").click().run()
    assert not app.exception and not app.error
    assert len(service.carregar().lancamentos) == 4
    assert service.resumir(service.carregar(), hoje()).saldo_total == Decimal("1069.50")
    app.run()
    assert len(service.carregar().lancamentos) == 4


def test_edicao_e_exclusao_exigem_confirmacao_na_interface(monkeypatch, service):
    app = iniciar(monkeypatch, service)
    transporte = next(x for x in service.carregar().lancamentos if x.categoria.nome == "Transporte")
    app.sidebar.radio[0].set_value("Lançamentos").run()
    next(x for x in app.selectbox if x.label == "Lançamento para editar").set_value(transporte.id).run()
    [x for x in app.text_input if x.label == "Valor (R$)"][1].set_value("150,00")
    [x for x in app.button if x.label == "Salvar lançamento"][1].click().run()
    assert not app.exception and not app.error
    assert service.resumir(service.carregar(), hoje()).saldo_total == Decimal("1050.00")
    next(x for x in app.button if x.label == "Excluir registro").click().run()
    assert len(service.carregar().lancamentos) == 3
    assert any("Marque a confirmação" in x.value for x in app.warning)
    app.checkbox[0].check()
    next(x for x in app.button if x.label == "Excluir registro").click().run()
    assert not app.exception and not app.error
    assert len(service.carregar().lancamentos) == 2
    assert service.resumir(service.carregar(), hoje()).saldo_total == Decimal("1200.00")
