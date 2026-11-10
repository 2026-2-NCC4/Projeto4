# app.py
# Dashboard CTI - Plataforma Analítica de Planejamento Financeiro
# PI Ciência de Dados - Entrega 2 / Projeto final - 4º semestre CCOMP (FECAP)
# Professor: Eduardo Savino Gomes
# Integrantes: Bruno Nobrega, Kaio Inglez, Mauricio Suster e Yuri Santana
#
# Arquivo principal: lê a base da Entrega 1, monta os filtros da barra lateral (valem para todas as
# páginas) e abre a página escolhida no menu.
# Para rodar:  python -m streamlit run app.py

import os
from datetime import datetime

import streamlit as st

from dados import ARQUIVO, carregar_base, validar_colunas, calcular_indicadores

st.set_page_config(page_title="Dashboard CTI", page_icon="📊", layout="wide")

# ---------------- leitura dos dados (com mensagens de erro) ----------------
if not os.path.exists(ARQUIVO):
    st.error("Base de dados não encontrada. Coloque o arquivo base_cti_processada.csv (Entrega 1) na pasta dados/.")
    st.stop()

base = carregar_base(ARQUIVO)
faltando = validar_colunas(base)
if faltando:
    st.error(f"A base não tem as colunas: {', '.join(faltando)}. Confira se é a base final da Entrega 1.")
    st.stop()

d = calcular_indicadores(base)
atualizado = datetime.fromtimestamp(os.path.getmtime(ARQUIVO)).strftime("%d/%m/%Y")

# ---------------- menu de páginas ----------------
paginas = {
    "Painel": [
        st.Page("paginas/visao_executiva.py", title="Visão executiva", icon=":material/dashboard:", default=True),
        st.Page("paginas/evolucao.py", title="Evolução e comparação", icon=":material/show_chart:"),
        st.Page("paginas/sensibilidade.py", title="Cenários e sensibilidade", icon=":material/tune:"),
        st.Page("paginas/caixa.py", title="Caixa e endividamento", icon=":material/account_balance:"),
    ],
    "Análises": [
        st.Page("paginas/relacoes.py", title="Relações entre variáveis", icon=":material/scatter_plot:"),
        st.Page("paginas/qualidade.py", title="Qualidade dos dados", icon=":material/fact_check:"),
        st.Page("paginas/notas.py", title="Notas metodológicas", icon=":material/menu_book:"),
    ],
}
navegacao = st.navigation(paginas)

# ---------------- filtros (barra lateral, valem para todas as páginas) ----------------
st.sidebar.header("Filtros")
grupos = ["Todos os cenários"] + sorted(d["grupo_cenario"].unique())
grupo = st.sidebar.radio("Grupo de cenários", grupos, key="grupo")
d_grupo = d if grupo == "Todos os cenários" else d[d["grupo_cenario"] == grupo]

cenario = st.sidebar.selectbox("Cenário", sorted(d_grupo["cenario"].unique()), key="cenario")
ano_ini, ano_fim = st.sidebar.slider("Período dos gráficos (anos)", 1, 12, (1, 12), key="periodo")
if ano_ini < ano_fim:   # o Ano 12 é atípico (fim da concessão), por isso o padrão é o Ano 11
    ano_ref = st.sidebar.slider("Ano de referência (cartões)", ano_ini, ano_fim, min(max(11, ano_ini), ano_fim),
                                key="ano_ref")
else:
    ano_ref = ano_fim
st.sidebar.caption(f"Fonte: CTI Global (Demonstrativo Fecap v3) · base atualizada em {atualizado}")

periodo = d_grupo[d_grupo["ano"].between(ano_ini, ano_fim)]
cen = periodo[periodo["cenario"] == cenario].set_index("ano")
if cen.empty:
    st.warning("Não há dados para os filtros escolhidos. Mude o grupo, o cenário ou o período.")
    st.stop()

# tudo que as páginas precisam fica guardado aqui
st.session_state["ctx"] = {
    "d": d, "d_grupo": d_grupo, "periodo": periodo, "cen": cen, "mediana": periodo.groupby("ano").median(numeric_only=True),
    "n_colunas_base": base.shape[1], "grupo": grupo, "cenario": cenario, "ano_ini": ano_ini, "ano_fim": ano_fim, "ano_ref": ano_ref, "atualizado": atualizado,
}

navegacao.run()
