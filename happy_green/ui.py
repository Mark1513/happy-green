"""Apresentação Streamlit: formulários chamam os serviços, sem SQL."""

from datetime import date
from decimal import Decimal
from html import escape

import pandas as pd
import streamlit as st

from . import bootstrap
from .clock import hoje as data_atual
from .domain import ZERO, TipoLancamento
from .errors import ConfigurationError, HappyGreenError
from .presentation import brl, ler_brl
from .services import ServicoFinanceiro

MESES = ("", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
         "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro")
PAGINAS = ("Visão geral", "Lançamentos", "Contas", "Categorias", "Orçamentos", "Resumo mensal", "Sobre o projeto")

STYLE = """
<style>
.hg-hero {background:linear-gradient(120deg,#0b422f,#167d53);border-radius:22px;
padding:32px 36px;margin:4px 0 24px;color:#fff;box-shadow:0 10px 28px #153e2112;}
.hg-hero h1 {color:#fff!important;padding:0;margin:6px 0 10px;font-size:2.6rem;letter-spacing:-1px;}
.hg-hero p {color:#deeee4;margin:0;max-width:650px;font-size:1.04rem;}
.hg-eyebrow {text-transform:uppercase;letter-spacing:2px;font-size:.74rem;font-weight:700;color:#bde8a5;}
.hg-brand {font-size:1.55rem;font-weight:800;letter-spacing:-.6px;color:#126343;margin-bottom:4px;}
.hg-note {color:#587164;font-size:.88rem;line-height:1.6;}
.hg-section {font-size:.72rem;font-weight:700;text-transform:uppercase;letter-spacing:1.6px;color:#678274;margin:10px 0;}
.hg-empty {padding:26px;border:1px dashed #aec6b5;border-radius:16px;background:#eef5ee;}
.hg-empty h3 {margin:0 0 6px;color:#185338;font-size:1.15rem;}
.hg-empty p {margin:0;color:#587164;}
@media(max-width:640px){.hg-hero{padding:24px 22px}.hg-hero h1{font-size:2rem}}
</style>
"""


def hero(titulo, subtitulo, etiqueta="Suas finanças, com mais leveza"):
    st.html(f'<section class="hg-hero"><div class="hg-eyebrow">{escape(etiqueta)}</div>'
            f'<h1>{escape(titulo)}</h1><p>{escape(subtitulo)}</p></section>')


def vazio(titulo, mensagem):
    st.html(f'<div class="hg-empty"><h3>{escape(titulo)}</h3><p>{escape(mensagem)}</p></div>')


def executar(acao, mensagem):
    try:
        acao()
    except HappyGreenError as exc:
        st.error(str(exc))
    else:
        st.session_state["flash"] = mensagem
        st.session_state["revision"] = st.session_state.get("revision", 0) + 1
        st.rerun()


def selecionar_mes(carteira, key):
    meses = {data_atual().replace(day=1)}
    meses.update(item.data.replace(day=1) for item in carteira.lancamentos)
    meses.update(item.mes for item in carteira.orcamentos)
    opcoes = sorted(meses, reverse=True)
    atual = data_atual().replace(day=1)
    return st.selectbox("Mês de referência", opcoes, index=opcoes.index(atual), key=key,
                        format_func=lambda item: f"{MESES[item.month]} de {item.year}")


def tabela_lancamentos(itens):
    if not itens:
        vazio("Nenhum lançamento neste período", "Registre uma movimentação ou ajuste os filtros para começar.")
        return
    linhas = [{"Data": item.data.strftime("%d/%m/%Y"), "Descrição": item.descricao,
               "Tipo": "Receita" if item.tipo == TipoLancamento.RECEITA else "Despesa",
               "Categoria": item.categoria.nome, "Conta": item.conta.nome,
               "Valor": brl(item.valor)} for item in itens]
    st.dataframe(pd.DataFrame(linhas), hide_index=True, width="stretch")


def mostrar_orcamento(orcamento, lancamentos):
    consumo = orcamento.calcular_consumo(lancamentos)
    percentual = consumo / orcamento.limite
    with st.container(border=True):
        st.markdown(f"**{orcamento.categoria.nome}**")
        st.caption(f"{brl(consumo)} utilizados de {brl(orcamento.limite)}")
        st.progress(float(min(percentual, Decimal(1))))
        if orcamento.limite_ultrapassado(lancamentos):
            st.warning(f"Limite ultrapassado em {brl(consumo - orcamento.limite)}")
        elif percentual >= Decimal("0.8"):
            st.info(f"Atenção: {percentual:.0%} do orçamento utilizado.")
        else:
            st.caption(f"Disponível: {brl(orcamento.limite - consumo)}")


def dashboard(service, carteira):
    hero("Seu dinheiro, bem cuidado.", "Acompanhe o que entra, entenda o que sai e dê espaço aos seus planos.")
    mes = selecionar_mes(carteira, "dashboard_mes")
    resumo = service.resumir(carteira, mes)
    cards = st.columns(4)
    for coluna, titulo, valor, ajuda in zip(
        cards, ("Saldo total atual", "Receitas do mês", "Despesas do mês", "Resultado do mês"),
        (resumo.saldo_total, resumo.receitas, resumo.despesas, resumo.resultado),
        ("Saldos iniciais + todas as movimentações realizadas.", "Entradas no mês selecionado.",
         "Saídas no mês selecionado.", "Receitas menos despesas do mês; não inclui saldos iniciais."),
    ):
        with coluna:
            st.metric(titulo, brl(valor), help=ajuda, border=True)
    st.write("")
    esquerda, direita = st.columns([1.4, 1], gap="large")
    with esquerda:
        st.subheader("Para onde foi seu dinheiro")
        gastos = {}
        for item in carteira.lancamentos:
            if item.data.replace(day=1) == mes and item.tipo == TipoLancamento.DESPESA:
                gastos[item.categoria.nome] = gastos.get(item.categoria.nome, ZERO) + item.valor
        if gastos:
            # float é usado SOMENTE na renderização do gráfico, nunca nos cálculos.
            frame = pd.DataFrame({"Categoria": list(gastos), "Despesas (R$)": [float(x) for x in gastos.values()]})
            st.bar_chart(frame, x="Categoria", y="Despesas (R$)", color="#159568", horizontal=True)
        else:
            vazio("Tudo começa com um registro", "Suas despesas por categoria aparecerão aqui.")
    with direita:
        st.subheader("De olho nos limites")
        orcamentos = [item for item in carteira.orcamentos if item.mes == mes]
        if not orcamentos:
            vazio("Planeje seu mês", "Defina limites na página Orçamentos e acompanhe seu progresso.")
        for item in orcamentos[:3]:
            mostrar_orcamento(item, carteira.lancamentos)
        if len(orcamentos) > 3:
            st.caption("Veja todos os limites na página Orçamentos.")
    st.subheader("Últimas movimentações do mês")
    itens = [item for item in carteira.lancamentos if item.data.replace(day=1) == mes]
    tabela_lancamentos(itens[:8])
    if not carteira.contas:
        st.info("Comece cadastrando uma conta e suas categorias, ou carregue a demonstração pela barra lateral.")


def confirmar_exclusao(service, entidade, item, nome):
    with st.expander("Excluir este registro"):
        with st.form(f"excluir_{entidade}_{item.id}"):
            st.write(f"Registro selecionado: {nome}")
            confirmar = st.checkbox("Confirmo a exclusão deste registro de demonstração.")
            enviado = st.form_submit_button("Excluir registro")
            if enviado:
                if not confirmar:
                    st.warning("Marque a confirmação antes de excluir.")
                else:
                    executar(lambda: service.excluir(entidade, item.id), "Registro excluído.")


def contas(service, carteira):
    hero("Cada conta no seu lugar.", "Organize sua carteira e acompanhe o saldo de cada conta.", "Contas financeiras")
    if carteira.contas:
        st.dataframe(pd.DataFrame([{"Conta": x.nome, "Saldo inicial": brl(x.saldo_inicial),
                                  "Saldo atual": brl(x.calcular_saldo(carteira.lancamentos))}
                                 for x in carteira.contas]), hide_index=True, width="stretch")
    else:
        vazio("Sua primeira conta", "Cadastre uma carteira, conta bancária ou reserva para começar.")
    nova, editar = st.tabs(["Nova conta", "Editar conta"])
    with nova:
        formulario_conta(service)
    with editar:
        if carteira.contas:
            mapa = {x.id: x for x in carteira.contas}
            id = st.selectbox("Conta para editar", list(mapa), format_func=lambda x: mapa[x].nome,
                              key="editar_conta_id")
            item = mapa[id]
            formulario_conta(service, item)
            confirmar_exclusao(service, "contas", item, item.nome)
        else:
            st.info("Cadastre uma conta para habilitar a edição.")


def formulario_conta(service, item=None):
    rev = st.session_state.get("revision", 0)
    with st.form(f"conta_{item.id if item else 'nova'}_{rev}"):
        nome = st.text_input("Nome da conta", value=item.nome if item else "", max_chars=80,
                             placeholder="Ex.: Minha carteira")
        saldo = st.text_input("Saldo inicial (R$)", value=str(item.saldo_inicial).replace(".", ",") if item else "0,00",
                             help="Informe o saldo anterior aos lançamentos. Pode ser negativo.")
        if st.form_submit_button("Salvar conta", type="primary"):
            executar(lambda: service.salvar_conta(nome, ler_brl(saldo), item.id if item else None), "Conta salva.")


def categorias(service, carteira):
    hero("Dê nome aos seus hábitos.", "Categorias ajudam a entender como você ganha e utiliza seu dinheiro.", "Categorias")
    if carteira.categorias:
        st.dataframe(pd.DataFrame([{"Categoria": x.nome, "Tipo": x.tipo.value.title()}
                                  for x in carteira.categorias]), hide_index=True, width="stretch")
    nova, editar = st.tabs(["Nova categoria", "Editar categoria"])
    with nova:
        formulario_categoria(service)
    with editar:
        if carteira.categorias:
            mapa = {x.id: x for x in carteira.categorias}
            id = st.selectbox("Categoria para editar", list(mapa),
                              format_func=lambda x: f"{mapa[x].nome} · {mapa[x].tipo.value.title()}",
                              key="editar_categoria_id")
            item = mapa[id]
            formulario_categoria(service, item)
            st.caption("O tipo de categorias vinculadas não pode ser alterado. O nome pode ser editado.")
            confirmar_exclusao(service, "categorias", item, item.nome)
        else:
            st.info("Cadastre uma categoria para habilitar a edição.")


def formulario_categoria(service, item=None):
    rev = st.session_state.get("revision", 0)
    with st.form(f"categoria_{item.id if item else 'nova'}_{rev}"):
        nome = st.text_input("Nome da categoria", value=item.nome if item else "", max_chars=80,
                             placeholder="Ex.: Alimentação, transporte, salário")
        tipos = list(TipoLancamento)
        tipo = st.selectbox("Tipo da categoria", tipos, index=tipos.index(item.tipo) if item else 1,
                            format_func=lambda x: x.value.title())
        if st.form_submit_button("Salvar categoria", type="primary"):
            executar(lambda: service.salvar_categoria(nome, tipo, item.id if item else None), "Categoria salva.")


def lancamentos(service, carteira):
    hero("Um registro, mais clareza.", "Registre suas movimentações e mantenha sua vida financeira em dia.", "Receitas e despesas")
    lista, novo, editar = st.tabs(["Consultar", "Novo lançamento", "Editar lançamento"])
    with lista:
        hoje = data_atual()
        col1, col2, col3 = st.columns(3)
        inicio = col1.date_input("Data inicial", hoje.replace(day=1), min_value=date(1900, 1, 1), max_value=date(2100, 12, 31))
        fim = col2.date_input("Data final", hoje, min_value=date(1900, 1, 1), max_value=date(2100, 12, 31))
        tipo = col3.selectbox("Tipo", [None, *TipoLancamento], format_func=lambda x: "Todos" if x is None else x.value.title())
        col1, col2 = st.columns(2)
        contas_map = {x.id: x for x in carteira.contas}
        categorias_map = {x.id: x for x in carteira.categorias}
        conta_id = col1.selectbox("Conta", [None, *contas_map], format_func=lambda x: "Todas" if x is None else contas_map[x].nome)
        categoria_id = col2.selectbox("Categoria", [None, *categorias_map],
                                     format_func=lambda x: "Todas" if x is None else f"{categorias_map[x].nome} · {categorias_map[x].tipo.value.title()}")
        try:
            itens = service.filtrar(carteira, inicio, fim, conta_id, categoria_id, tipo)
            st.caption(f"{len(itens)} movimentação(ões) encontradas")
            tabela_lancamentos(itens)
            if itens:
                resultado = sum((x.calcular_impacto_no_saldo() for x in itens), ZERO)
                st.markdown(f"**Resultado dos lançamentos filtrados: {brl(resultado)}**")
        except HappyGreenError as exc:
            st.error(str(exc))
    with novo:
        formulario_lancamento(service, carteira)
    with editar:
        if carteira.lancamentos:
            mapa = {x.id: x for x in carteira.lancamentos}
            id = st.selectbox("Lançamento para editar", list(mapa),
                              format_func=lambda x: f"{mapa[x].data:%d/%m/%Y} · {mapa[x].descricao} · {brl(mapa[x].valor)}",
                              key="editar_lancamento_id")
            item = mapa[id]
            formulario_lancamento(service, carteira, item)
            confirmar_exclusao(service, "lancamentos", item, item.descricao)
        else:
            st.info("Registre uma movimentação para habilitar a edição.")


def formulario_lancamento(service, carteira, item=None):
    if not carteira.contas:
        st.info("Cadastre uma conta antes de registrar movimentações.")
        return
    rev = st.session_state.get("revision", 0)
    prefix = f"lancamento_{item.id if item else 'novo'}_{rev}"
    tipos = list(TipoLancamento)
    tipo = st.radio("Tipo do lançamento", tipos, index=tipos.index(item.tipo) if item else 1,
                    format_func=lambda x: x.value.title(), horizontal=True, key=f"tipo_{prefix}")
    categorias_map = {x.id: x for x in carteira.categorias if x.tipo == tipo}
    if not categorias_map:
        st.info(f"Cadastre uma categoria de {tipo.value.lower()} antes de continuar.")
        return
    contas_map = {x.id: x for x in carteira.contas}
    with st.form(prefix):
        descricao = st.text_input("Descrição", value=item.descricao if item else "", max_chars=160,
                                  placeholder="Ex.: Compras do mês")
        col1, col2 = st.columns(2)
        valor = col1.text_input("Valor (R$)", value=str(item.valor).replace(".", ",") if item else "",
                               placeholder="Ex.: 120,00")
        data = col2.date_input("Data da movimentação", value=item.data if item else data_atual(),
                              min_value=date(1900, 1, 1), max_value=data_atual())
        conta_index = list(contas_map).index(item.conta.id) if item and item.conta.id in contas_map else 0
        categoria_index = list(categorias_map).index(item.categoria.id) if item and item.categoria.id in categorias_map else 0
        conta_id = st.selectbox("Conta do lançamento", list(contas_map), index=conta_index,
                                format_func=lambda x: contas_map[x].nome)
        categoria_id = st.selectbox("Categoria do lançamento", list(categorias_map), index=categoria_index,
                                    format_func=lambda x: categorias_map[x].nome)
        if st.form_submit_button("Salvar lançamento", type="primary"):
            executar(lambda: service.salvar_lancamento(conta_id, categoria_id, tipo, descricao,
                                                       ler_brl(valor), data, item.id if item else None), "Lançamento salvo.")


def orcamentos(service, carteira):
    hero("Planejar também é cuidar.", "Defina limites possíveis e acompanhe seus gastos sem perder o controle.", "Orçamentos mensais")
    mes = selecionar_mes(carteira, "orcamentos_mes")
    itens = [x for x in carteira.orcamentos if x.mes == mes]
    if not itens:
        vazio("Seu mês pode ter um plano", "Crie um limite por categoria de despesa no formulário abaixo.")
    for item in itens:
        mostrar_orcamento(item, carteira.lancamentos)
    st.subheader("Definir ou atualizar um limite")
    mapa = {x.id: x for x in carteira.categorias if x.tipo == TipoLancamento.DESPESA}
    if mapa:
        rev = st.session_state.get("revision", 0)
        with st.form(f"orcamento_{rev}"):
            categoria = st.selectbox("Categoria do orçamento", list(mapa), format_func=lambda x: mapa[x].nome)
            referencia = st.date_input("Mês do orçamento", data_atual().replace(day=1),
                                       min_value=date(1900, 1, 1), max_value=date(2100, 12, 31),
                                       help="Qualquer dia escolhido representa o mês inteiro.")
            limite = st.text_input("Limite mensal (R$)", placeholder="Ex.: 500,00")
            st.caption("Salvar novamente a mesma categoria e mês atualiza o limite existente.")
            if st.form_submit_button("Salvar orçamento", type="primary"):
                executar(lambda: service.salvar_orcamento(categoria, referencia, ler_brl(limite)), "Orçamento salvo.")
    else:
        st.info("Cadastre uma categoria de despesa para definir orçamentos.")
    if itens:
        mapa_orc = {x.id: x for x in itens}
        id = st.selectbox("Orçamento para excluir", list(mapa_orc), format_func=lambda x: mapa_orc[x].categoria.nome,
                          key="excluir_orcamento_id")
        confirmar_exclusao(service, "orcamentos", mapa_orc[id], mapa_orc[id].categoria.nome)


def resumo_mensal(service, carteira):
    hero("Seu mês em perspectiva.", "Transforme seus registros em uma visão clara das suas escolhas.", "Resumo mensal")
    mes = selecionar_mes(carteira, "resumo_mes")
    resumo = service.resumir(carteira, mes)
    a, b, c = st.columns(3)
    a.metric("Receitas", brl(resumo.receitas), border=True)
    b.metric("Despesas", brl(resumo.despesas), border=True)
    c.metric("Resultado mensal", brl(resumo.resultado), border=True)
    st.caption("O resultado mensal considera apenas os lançamentos do mês. Saldos iniciais ficam fora deste resultado.")
    grupos = {}
    for item in carteira.lancamentos:
        if item.data.replace(day=1) == mes:
            key = (item.categoria.id, item.tipo)
            if key not in grupos:
                grupos[key] = {"Categoria": item.categoria.nome, "Tipo": item.tipo.value.title(), "valor": ZERO}
            grupos[key]["valor"] += item.valor
    if grupos:
        dados = [{"Categoria": x["Categoria"], "Tipo": x["Tipo"], "Total": brl(x["valor"])} for x in grupos.values()]
        st.dataframe(pd.DataFrame(dados), hide_index=True, width="stretch")
    else:
        vazio("Um mês ainda em branco", "Os totais por categoria aparecerão após registrar movimentações.")


def sobre():
    hero("Happy Green", "Um projeto para aprender orientação a objetos cuidando das finanças.", "Sobre o projeto")
    st.markdown("""Esta é uma **demonstração acadêmica pública**, com dados fictícios compartilhados.
    A moeda utilizada é o **real brasileiro (BRL)**. Os lançamentos representam movimentações já realizadas.

    **Como a POO participa do sistema:**
    - `ContaFinanceira` calcula seu saldo colaborando com os lançamentos.
    - `Lancamento` define um contrato abstrato.
    - `Receita` e `Despesa` sobrescrevem `calcular_impacto_no_saldo()`.
    - `OrcamentoMensal` associa categoria, mês e limite para avaliar o consumo.
    - Serviços coordenam os casos de uso; repositórios cuidam da persistência.

    As regras financeiras podem ser testadas sem a interface e sem o banco.
    O README inclui o diagrama de classes, as etapas propostas e o roteiro de apresentação.
    """)


def configuracao(mensagem):
    hero("Vamos preparar seu jardim.", "O Happy Green está instalado. Falta conectar o banco para começar.", "Configuração inicial")
    st.warning(mensagem)
    with st.expander("Como configurar a conexão", expanded=True):
        st.markdown("""1. Crie ou selecione seu projeto no **Supabase**.
2. No SQL Editor, execute `migrations/001_initial.sql` deste repositório.
3. Em **Connect → Session pooler**, copie host, porta e usuário.
4. Configure a seção `database` em **Settings → Secrets** na hospedagem,
   ou no arquivo local `.streamlit/secrets.toml`, conforme o exemplo do repositório.
5. Recarregue a aplicação.

As instruções completas estão em `docs/PUBLICACAO.md`. A senha deve ser configurada apenas no painel protegido ou arquivo local ignorado pelo Git.
""")


def main():
    st.set_page_config(page_title="Happy Green · Suas finanças, com mais leveza", page_icon="🌿", layout="wide")
    st.html(STYLE)
    with st.sidebar:
        st.html('<div class="hg-brand">🌿 Happy Green</div><div class="hg-note">Pequenos registros. Grandes planos.</div>')
        st.divider()
        pagina = st.radio("Navegação", PAGINAS, label_visibility="collapsed", key="pagina")
        st.divider()
        st.caption("DEMONSTRAÇÃO ACADÊMICA")
        st.caption("Dados fictícios compartilhados. Outros visitantes podem editar os registros.")
        if st.button("Atualizar dados", width="stretch"):
            st.rerun()
    if "flash" in st.session_state:
        st.success(st.session_state.pop("flash"))
    if pagina == "Sobre o projeto":
        sobre()
        return
    try:
        service = bootstrap.get_service()
        carteira = service.carregar()
    except ConfigurationError as exc:
        configuracao(str(exc))
        return
    except HappyGreenError as exc:
        st.error(str(exc))
        st.info("Use Atualizar dados para tentar novamente. A configuração está documentada no README.")
        return
    with st.sidebar:
        if not any((carteira.contas, carteira.categorias, carteira.lancamentos, carteira.orcamentos)):
            st.caption("Primeiro acesso? Explore os dados de exemplo.")
            if st.button("Carregar demonstração", width="stretch"):
                executar(service.carregar_demonstracao, "Demonstração carregada. Bem-vindo ao Happy Green!")
    rotas = {"Visão geral": dashboard, "Lançamentos": lancamentos, "Contas": contas,
             "Categorias": categorias, "Orçamentos": orcamentos, "Resumo mensal": resumo_mensal}
    rotas[pagina](service, carteira)
    st.divider()
    st.caption("Happy Green · Gestão financeira pessoal · Valores em reais (BRL) · Projeto acadêmico de POO")

