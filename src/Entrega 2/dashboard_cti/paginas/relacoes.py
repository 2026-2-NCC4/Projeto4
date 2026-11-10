# paginas/relacoes.py - correlação e regressão linear entre as variáveis (contribuição da Análise Inferencial)

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from dados import ols
from formatos import AZUL, CINZA, LARANJA, VERDE, br, cabecalho, formatar, layout, md

ctx = st.session_state["ctx"]
d_grupo = ctx["d_grupo"]
todos_grupos = ctx["grupo"] == "Todos os cenários"

cabecalho("Relações entre variáveis", ctx, "O que explica a diferença de lucro entre os cenários? Esta página "
          "mostra as correlações e os modelos de regressão linear da entrega de Análise Inferencial.")

VARIAVEIS = {"receita_liquida": "Receita líquida", "custos": "Custos", "ebitda": "EBITDA",
             "depreciacao_amortizacao": "Depreciação e amortização", "resultado_financeiro": "Resultado financeiro",
             "lucro_liquido": "Lucro líquido", "caixa": "Caixa", "divida_bruta": "Dívida bruta"}
c1, c2 = st.columns(2)
ano = c1.slider("Ano da análise", 1, 12, 6, help="O relatório de Análise Inferencial usa o Ano 6, meio da concessão.")
x_col = c2.selectbox("Variável explicativa (eixo x)", ["receita_liquida", "custos", "ebitda", "resultado_financeiro",
                                                        "depreciacao_amortizacao"], format_func=VARIAVEIS.get)
no_ano = d_grupo[d_grupo["ano"] == ano]

# ---------------- regressão simples ----------------
st.subheader(f"Regressão simples: lucro líquido x {VARIAVEIS[x_col].lower()} – Ano {ano}")
coef, r2, rmse, n = ols(no_ano, "lucro_liquido", [x_col])
b0, b1 = coef.loc["Intercepto", "coef"], coef.loc[x_col, "coef"]
fig = px.scatter(no_ano, x=x_col, y="lucro_liquido", color="grupo_cenario", opacity=0.6,
                 color_discrete_sequence=[AZUL, LARANJA], labels={x_col: VARIAVEIS[x_col], "grupo_cenario": "Grupo"})
xs = np.linspace(no_ano[x_col].min(), no_ano[x_col].max(), 50)
fig.add_trace(go.Scatter(x=xs, y=b0 + b1 * xs, name="Reta ajustada", mode="lines", line=dict(color=VERDE, width=3)))
fig.update_traces(marker=dict(size=6), selector=dict(mode="markers"))
st.plotly_chart(layout(fig, f"Lucro líquido x {VARIAVEIS[x_col].lower()} (cada ponto é um cenário)", "Lucro líquido (R$ milhões)",
                       430, f"{VARIAVEIS[x_col]} (R$ milhões)", False), width="stretch")
c = st.columns(4)
c[0].metric("Inclinação (β1)", br(b1, 3), help="Quanto o lucro muda, em média, para cada R$ 1 milhão a mais da variável")
c[1].metric("R²", br(r2, 3), help="Parte da variação do lucro explicada pelo modelo (0 a 1)")
c[2].metric("Erro típico (RMSE)", formatar(rmse, "rs"))
c[3].metric("Cenários (n)", br(n))
st.write(md(f"Cada R\\$ 1 milhão a mais de {VARIAVEIS[x_col].lower()} está associado, em média, a "
         f"**{br(b1, 2)} milhão {'a mais' if b1 >= 0 else 'a menos'}** de lucro líquido "
         f"(IC 95%: {br(coef.loc[x_col, 'ic_min'], 3)} a {br(coef.loc[x_col, 'ic_max'], 3)}). "
         f"O modelo explica **{br(r2 * 100, 1)}%** da variação do lucro entre os cenários."))

# ---------------- regressão múltipla ----------------
st.subheader(f"Regressão múltipla – Ano {ano}")
xs_multi = ["receita_liquida", "custos"] + (["grupo2"] if todos_grupos else [])
coef_m, r2_m, rmse_m, n_m = ols(no_ano, "lucro_liquido", xs_multi)
formula = "lucro = β0 + β1·receita líquida + β2·custos" + (" + β3·grupo 1001-1200" if todos_grupos else "")
st.write(md(f"Modelo: {formula}. R² = **{br(r2_m, 3)}**, erro típico = **{formatar(rmse_m, 'rs')}**, n = {br(n_m)}."))
nomes = {"Intercepto": "Intercepto", "receita_liquida": "Receita líquida", "custos": "Custos",
         "grupo2": "Grupo 1001-1200 (dummy)"}
leitura = {"Intercepto": "Só posiciona a reta, sem leitura prática",
           "receita_liquida": "R$ 1 mi a mais de receita, com custos e grupo iguais",
           "custos": "R$ 1 mi a mais de custos, com receita e grupo iguais",
           "grupo2": "Diferença média de lucro dos cenários 1001-1200"}
st.dataframe(pd.DataFrame({"Variável": [nomes[i] for i in coef_m.index],
                           "Coeficiente": [br(v, 3) for v in coef_m["coef"]],
                           "IC 95%": [f"{br(a, 3)} a {br(b, 3)}" for a, b in zip(coef_m["ic_min"], coef_m["ic_max"])],
                           "Como ler": [leitura[i] for i in coef_m.index]}), hide_index=True, width="stretch")
if not todos_grupos:
    st.caption("Com um grupo só, a dummy de grupo sai do modelo.")
st.caption("O coeficiente da receita fica perto de 0,66 = 1 − 34% (alíquota de IR/CSLL): de cada real a mais de "
           "receita, cerca de 65 centavos viram lucro. IC 95% com erro-padrão comum; o relatório de Análise Inferencial "
           "traz os diagnósticos completos (Breusch-Pagan, Jarque-Bera e erros robustos HC3).")

# ---------------- estabilidade e correlação ----------------
linhas = []
for a in range(1, 13):
    cf, r2_a, _, _ = ols(d_grupo[d_grupo["ano"] == a], "lucro_liquido", xs_multi)
    linhas.append({"ano": a, "coef": cf.loc["receita_liquida", "coef"], "min": cf.loc["receita_liquida", "ic_min"],
                   "max": cf.loc["receita_liquida", "ic_max"], "r2": r2_a})
estab = pd.DataFrame(linhas).set_index("ano")
fig = go.Figure()
fig.add_trace(go.Scatter(x=estab.index, y=estab["coef"], mode="lines+markers", name="Coeficiente da receita",
                         line=dict(color=AZUL, width=3),
                         error_y=dict(type="data", symmetric=False, array=estab["max"] - estab["coef"],
                                      arrayminus=estab["coef"] - estab["min"], color=AZUL)))
fig.add_hline(y=0.66, line_dash="dot", line_color=CINZA, annotation_text="0,66 = 1 − 34%", annotation_position="bottom right")
st.plotly_chart(layout(fig, "Coeficiente da receita no modelo múltiplo, ano a ano (com IC 95%)", "coeficiente", 400),
                width="stretch")

cols = list(VARIAVEIS)
corr = no_ano[cols].corr().rename(index=VARIAVEIS, columns=VARIAVEIS)
fig = px.imshow(corr.round(2), text_auto=".2f", color_continuous_scale="RdBu", zmin=-1, zmax=1, aspect="auto")
fig.update_layout(title=f"Correlação entre as variáveis – Ano {ano}", height=520, margin=dict(l=10, r=10, t=60, b=10),
                  coloraxis_showscale=False, separators=",.", font=dict(size=13))
fig.update_xaxes(side="bottom", tickangle=-30)
st.plotly_chart(fig, width="stretch")
st.caption("Perto de 1: as duas variáveis sobem juntas. Perto de −1: quando uma sobe, a outra desce. Perto de 0: pouca relação linear.")

st.caption("Correlação não é causa: os modelos mostram associações dentro dos cenários simulados pela CTI.")
