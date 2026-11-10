# paginas/visao_executiva.py - os 5 KPIs principais, indicadores complementares e resumo do ano

import plotly.graph_objects as go
import streamlit as st

from dados import KPIS, COMPLEMENTARES, MENOR_MELHOR
from formatos import AZUL, CINZA, LARANJA, VERDE, br, cabecalho, cartoes, diferenca, formatar, layout, md

ctx = st.session_state["ctx"]
cen, mediana, ano = ctx["cen"], ctx["mediana"], ctx["ano_ref"]
linha, ref = cen.loc[ano], mediana.loc[ano]
no_ano = ctx["d_grupo"][ctx["d_grupo"]["ano"] == ano]

cabecalho("Visão executiva", ctx)

# ---------------- 5 KPIs principais ----------------
st.subheader(f"KPIs principais – Ano {ano}")
st.caption("Abaixo de cada valor: diferença para a mediana dos cenários do grupo no mesmo ano. Passe o mouse no ? para ver a fórmula.")
cartoes([(f"{c} · {n}", formatar(linha[col], t), diferenca(linha[col], ref[col], t), f, col in MENOR_MELHOR)
         for c, n, col, t, f in KPIS])

# ---------------- resumo em texto ----------------
st.subheader("O que os números dizem")
dif_receita = linha["receita_liquida"] / ref["receita_liquida"] - 1
acima_lucro = (no_ano["lucro_liquido"] < linha["lucro_liquido"]).mean()
frases = [
    f"A receita líquida foi de **{formatar(linha['receita_liquida'], 'rs')}**, "
    f"{br(abs(dif_receita) * 100, 1)}% {'acima' if dif_receita >= 0 else 'abaixo'} da mediana do grupo.",
    f"De cada R\\$ 100 de receita líquida, **R\\$ {br(linha['margem_ebitda'] * 100)}** viram EBITDA e "
    f"**R\\$ {br(linha['margem_liquida'] * 100)}** viram lucro líquido.",
    f"O lucro líquido de **{formatar(linha['lucro_liquido'], 'rs')}** está acima de **{br(acima_lucro * 100, 1)}%** "
    f"dos cenários do grupo neste ano.",
]
if linha["divida_liquida_ebitda"] < 0:
    frases.append("O caixa é maior que a dívida, então a dívida líquida é negativa: a empresa não depende de "
                  "dívida neste ano.")
else:
    frases.append(f"Com o EBITDA deste ano, a dívida líquida seria paga em **{br(linha['divida_liquida_ebitda'], 1)} anos**.")
if linha["lucro_liquido"] > 0:
    frases.append(f"Os dividendos pagos equivalem a **{br(linha['payout'] * 100)}%** do lucro líquido do ano.")
st.markdown(md("\n".join(f"- {f}" for f in frases)))

# ---------------- complementares ----------------
st.subheader(f"Indicadores complementares – Ano {ano}")
escolhidos = ["lucro_liquido", "divida_bruta", "endividamento_geral", "payout", "geracao_caixa", "caixa"]
itens = [x for x in COMPLEMENTARES if x[2] in escolhidos]
cartoes([(f"{c} · {n}" if c != "–" else n, formatar(linha[col], t), diferenca(linha[col], ref[col], t), f,
          None if col == "payout" else col in MENOR_MELHOR) for c, n, col, t, f in itens])

# ---------------- gráficos ----------------
col1, col2 = st.columns(2)
fig = go.Figure()
for col, nome, cor in [("receita_liquida", "Receita líquida", AZUL), ("ebitda", "EBITDA", VERDE),
                       ("lucro_liquido", "Lucro líquido", LARANJA)]:
    fig.add_trace(go.Bar(x=cen.index, y=cen[col], name=nome, marker_color=cor))
fig.update_layout(barmode="group")
col1.plotly_chart(layout(fig, f"Receita, EBITDA e lucro – cenário {ctx['cenario']}", "R$ milhões"), width="stretch")

fig = go.Figure()
for col, nome, cor in [("margem_ebitda", "Margem EBITDA", VERDE), ("margem_liquida", "Margem líquida", LARANJA)]:
    fig.add_trace(go.Scatter(x=cen.index, y=cen[col] * 100, name=nome, mode="lines+markers", line=dict(color=cor, width=3)))
    fig.add_trace(go.Scatter(x=mediana.index, y=mediana[col] * 100, name=f"{nome} (mediana)",
                             mode="lines", line=dict(color=cor, width=1.5, dash="dash")))
col2.plotly_chart(layout(fig, "Margens – cenário (linha cheia) e mediana do grupo (tracejada)", "%"), width="stretch")
