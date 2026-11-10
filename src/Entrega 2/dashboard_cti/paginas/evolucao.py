# paginas/evolucao.py - evolução no tempo, comparação entre dois cenários, distribuição e ranking

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from dados import KPIS, TODOS, MENOR_MELHOR
from formatos import AZUL, CINZA, LARANJA, VERDE, UNIDADE, br, cabecalho, escala, formatar, layout, md

ctx = st.session_state["ctx"]
cen, periodo, d_grupo, ano = ctx["cen"], ctx["periodo"], ctx["d_grupo"], ctx["ano_ref"]

cabecalho("Evolução e comparação", ctx, "Veja como um indicador muda ao longo da concessão e compare o cenário "
          "escolhido com a mediana, com a faixa onde ficam 80% dos cenários e com outro cenário.")

nomes = [f"{c} · {n}" if c != "–" else n for c, n, _, _, _ in TODOS]
c1, c2 = st.columns(2)
escolhido = c1.selectbox("Indicador", nomes, index=0)
_, nome_kpi, col_kpi, tipo, formula = TODOS[nomes.index(escolhido)]
outros = [c for c in sorted(d_grupo["cenario"].unique()) if c != ctx["cenario"]]
comparar = c2.selectbox("Comparar com o cenário", ["Nenhum"] + outros)
k = escala(tipo)

# ---------------- evolução ----------------
faixa = periodo.groupby("ano")[col_kpi].quantile([0.1, 0.5, 0.9]).unstack() * k
fig = go.Figure()
fig.add_trace(go.Scatter(x=faixa.index, y=faixa[0.9], line=dict(width=0), showlegend=False, hoverinfo="skip"))
fig.add_trace(go.Scatter(x=faixa.index, y=faixa[0.1], fill="tonexty", line=dict(width=0), fillcolor="rgba(46,94,140,0.15)",
                         name="80% dos cenários (P10 a P90)", hoverinfo="skip"))
fig.add_trace(go.Scatter(x=faixa.index, y=faixa[0.5], name="Mediana do grupo", line=dict(color=CINZA, dash="dash", width=2)))
fig.add_trace(go.Scatter(x=cen.index, y=cen[col_kpi] * k, name=f"Cenário {ctx['cenario']}", mode="lines+markers",
                         line=dict(color=VERDE, width=3)))
if comparar != "Nenhum":
    outro = periodo[periodo["cenario"] == comparar].set_index("ano")
    fig.add_trace(go.Scatter(x=outro.index, y=outro[col_kpi] * k, name=f"Cenário {comparar}", mode="lines+markers",
                             line=dict(color=LARANJA, width=3)))
st.plotly_chart(layout(fig, f"{nome_kpi} por ano", UNIDADE[tipo]), width="stretch")
st.caption(f"Fórmula: {formula}.")

# ---------------- comparação entre dois cenários ----------------
if comparar != "Nenhum":
    st.subheader(f"Cenário {ctx['cenario']} x cenário {comparar} – Ano {ano}")
    a = cen.loc[ano]
    b = periodo[(periodo["cenario"] == comparar) & (periodo["ano"] == ano)].iloc[0]
    tabela = pd.DataFrame([{"Indicador": f"{c} · {n}", f"Cenário {ctx['cenario']}": formatar(a[col], t),
                            f"Cenário {comparar}": formatar(b[col], t),
                            "Diferença": (f"{br((a[col] - b[col]) * 100, 1)} p.p." if t == "pct" else
                                          formatar(a[col] - b[col], t))}
                           for c, n, col, t, _ in KPIS])
    st.dataframe(tabela, hide_index=True, width="stretch")

# ---------------- distribuição e ranking ----------------
st.subheader(f"Onde o cenário fica entre os outros – Ano {ano}")
no_ano = d_grupo[d_grupo["ano"] == ano]
valor = cen.loc[ano, col_kpi]
acima = (no_ano[col_kpi] < valor).mean()
st.write(md(f"O cenário {ctx['cenario']} tem **{nome_kpi} = {formatar(valor, tipo)}** e fica acima de "
         f"**{br(acima * 100, 1)}%** dos cenários do grupo ({ctx['grupo'].lower()})."))

col1, col2 = st.columns(2)
fig = px.histogram(x=no_ano[col_kpi] * k, nbins=40, color_discrete_sequence=[AZUL])
fig.add_vline(x=valor * k, line_color=LARANJA, line_width=3, annotation_text=f"cenário {ctx['cenario']}",
              annotation_position="top")
col1.plotly_chart(layout(fig, f"{nome_kpi} nos cenários do grupo", "Quantidade de cenários", 400, UNIDADE[tipo], False),
                  width="stretch")
todos_ano = ctx["d"][ctx["d"]["ano"] == ano]
fig = px.box(todos_ano, x="grupo_cenario", y=todos_ano[col_kpi] * k, color="grupo_cenario",
             color_discrete_sequence=[AZUL, LARANJA])
fig.update_layout(showlegend=False)
col2.plotly_chart(layout(fig, f"{nome_kpi} por grupo de cenários", UNIDADE[tipo], 400, "", False), width="stretch")

melhor_primeiro = col_kpi not in MENOR_MELHOR
ordem = no_ano.sort_values(col_kpi, ascending=not melhor_primeiro)
col1, col2 = st.columns(2)
for coluna, titulo, parte in [(col1, "5 melhores cenários", ordem.head(5)), (col2, "5 piores cenários", ordem.tail(5)[::-1])]:
    coluna.markdown(f"**{titulo} – {nome_kpi}**")
    coluna.dataframe(pd.DataFrame({"Cenário": parte["cenario"].values, "Grupo": parte["grupo_cenario"].values,
                                   nome_kpi: [formatar(v, tipo) for v in parte[col_kpi]]}),
                     hide_index=True, width="stretch")

# ---------------- tabela ----------------
with st.expander("Ver tabela ano a ano"):
    tabela = pd.DataFrame({f"Cenário {ctx['cenario']}": cen[col_kpi], "Mediana": faixa[0.5] / k,
                           "P10": faixa[0.1] / k, "P90": faixa[0.9] / k})
    if comparar != "Nenhum":
        tabela.insert(1, f"Cenário {comparar}", outro[col_kpi])
    st.dataframe(tabela.map(lambda v: formatar(v, tipo)).rename(index=lambda a: f"Ano {a}"), width="stretch")
    st.download_button("Baixar tabela (CSV)", tabela.to_csv(sep=";", decimal=",").encode("utf-8-sig"),
                       file_name=f"{col_kpi}_cenario_{ctx['cenario']}.csv", mime="text/csv")
