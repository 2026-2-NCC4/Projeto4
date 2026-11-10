# paginas/caixa.py - caixa, dívida, dividendos e investimentos

import plotly.graph_objects as go
import streamlit as st

from dados import MENOR_MELHOR
from formatos import AZUL, CINZA, LARANJA, VERDE, VERMELHO, br, cabecalho, cartoes, diferenca, formatar, layout

ctx = st.session_state["ctx"]
cen, mediana, ano = ctx["cen"], ctx["mediana"], ctx["ano_ref"]
linha, ref = cen.loc[ano], mediana.loc[ano]

cabecalho("Caixa e endividamento", ctx, "Quanto caixa a concessionária tem, quanto deve e para onde vai o dinheiro "
          "(dividendos e investimentos).")

st.subheader(f"Posição no Ano {ano}")
cartoes([(n, formatar(linha[col], "rs"), diferenca(linha[col], ref[col], "rs"), ajuda, col in MENOR_MELHOR)
         for n, col, ajuda in [("Caixa", "caixa", "Disponível no fim do ano"),
                               ("C01 · Dívida bruta", "divida_bruta", "Empréstimos e financiamentos"),
                               ("Dívida líquida", "divida_liquida", "Dívida bruta − caixa")]])
st.subheader(f"Acumulado nos Anos {ctx['ano_ini']} a {ctx['ano_fim']}")
soma, soma_med = cen.sum(numeric_only=True), mediana.sum(numeric_only=True)
cartoes([(n, formatar(soma[col], "rs"), diferenca(soma[col], soma_med[col], "rs"), ajuda, False)
         for n, col, ajuda in [("Dividendos pagos", "dividendos", "Soma dos dividendos pagos no período"),
                               ("Investimentos", "investimentos", "Soma dos investimentos pagos no período"),
                               ("Geração de caixa", "geracao_caixa", "Soma da variação do caixa no período")]])

col1, col2 = st.columns(2)
fig = go.Figure()
for col, nome, cor in [("divida_bruta", "Dívida bruta", VERMELHO), ("caixa", "Caixa", VERDE), ("divida_liquida", "Dívida líquida", AZUL)]:
    fig.add_trace(go.Scatter(x=cen.index, y=cen[col], name=nome, mode="lines+markers", line=dict(color=cor, width=3)))
fig.add_hline(y=0, line_color=CINZA)
col1.plotly_chart(layout(fig, f"Dívida e caixa – cenário {ctx['cenario']}", "R$ milhões"), width="stretch")

fig = go.Figure()
fig.add_trace(go.Bar(x=cen.index, y=cen["dividendos"], name="Dividendos pagos", marker_color=LARANJA))
fig.add_trace(go.Bar(x=cen.index, y=cen["investimentos"], name="Investimentos", marker_color=AZUL))
fig.add_trace(go.Scatter(x=cen.index, y=cen["geracao_caixa"], name="Geração de caixa", mode="lines+markers",
                         line=dict(color=VERDE, width=3)))
fig.update_layout(barmode="group")
col2.plotly_chart(layout(fig, "Para onde vai o dinheiro", "R$ milhões"), width="stretch")

col1, col2 = st.columns(2)
for coluna, col, nome, titulo in [(col1, "divida_liquida_ebitda", "C08 · Dívida líquida / EBITDA", "vezes"),
                                  (col2, "payout", "Payout (dividendos / lucro)", "%")]:
    k = 100 if titulo == "%" else 1
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=cen.index, y=cen[col] * k, name=f"Cenário {ctx['cenario']}", mode="lines+markers",
                             line=dict(color=AZUL, width=3)))
    fig.add_trace(go.Scatter(x=mediana.index, y=mediana[col] * k, name="Mediana do grupo", line=dict(color=CINZA, dash="dash")))
    if col == "divida_liquida_ebitda":
        fig.add_hline(y=0, line_color=CINZA)
    else:
        fig.add_hline(y=100, line_color=CINZA, line_dash="dot", annotation_text="100% do lucro", annotation_position="top left")
    coluna.plotly_chart(layout(fig, nome, titulo, 380), width="stretch")

st.caption("Dívida líquida / EBITDA abaixo de zero quer dizer que o caixa é maior que a dívida. Payout acima de 100% quer "
           "dizer que a empresa pagou mais dividendos do que lucrou no ano, usando caixa de anos anteriores.")
