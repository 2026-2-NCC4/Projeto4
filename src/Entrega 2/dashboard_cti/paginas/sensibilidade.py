# paginas/sensibilidade.py - cenários pessimista/realista/otimista, simulador "e se?" e o que mais mexe no lucro

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from dados import KPIS, MENOR_MELHOR, lucro_simulado
from formatos import AZUL, CINZA, LARANJA, VERDE, VERMELHO, UNIDADE, br, cabecalho, cartoes, delta_br, escala, formatar, layout, md

ctx = st.session_state["ctx"]
cen, periodo, ano = ctx["cen"], ctx["periodo"], ctx["ano_ref"]
linha = cen.loc[ano]

cabecalho("Cenários e sensibilidade", ctx)

# ---------------- 1. pessimista, realista e otimista ----------------
st.subheader("Cenários pessimista, realista e otimista")
st.write("Entre os cenários do grupo, o pessimista é o percentil 10 (só 10% dos cenários ficam piores), o realista é "
         "a mediana e o otimista é o percentil 90. Nos indicadores em que menor é melhor (dívida), a ordem se inverte.")
opcoes = [("A13", "Lucro líquido", "lucro_liquido", "rs", "")] + KPIS
nomes = [f"{c} · {n}" for c, n, _, _, _ in opcoes]
escolhido = st.selectbox("Indicador", nomes, index=0)
_, nome_kpi, col_kpi, tipo, _ = opcoes[nomes.index(escolhido)]
k = escala(tipo)
q = periodo.groupby("ano")[col_kpi].quantile([0.1, 0.5, 0.9]).unstack()
pess, otim = (q[0.9], q[0.1]) if col_kpi in MENOR_MELHOR else (q[0.1], q[0.9])
fig = go.Figure()
for serie, nome, cor, traco in [(otim, "Otimista", VERDE, "dash"), (q[0.5], "Realista (mediana)", CINZA, "dash"),
                                (pess, "Pessimista", VERMELHO, "dash")]:
    fig.add_trace(go.Scatter(x=serie.index, y=serie * k, name=nome, mode="lines", line=dict(color=cor, width=2, dash=traco)))
fig.add_trace(go.Scatter(x=cen.index, y=cen[col_kpi] * k, name=f"Cenário {ctx['cenario']}", mode="lines+markers",
                         line=dict(color=AZUL, width=3)))
st.plotly_chart(layout(fig, f"{nome_kpi}: pessimista, realista e otimista", UNIDADE[tipo]), width="stretch")
if ano in q.index:
    st.caption(md(f"No Ano {ano}, o indicador {nome_kpi} vai de "
               f"{formatar(pess[ano], tipo)} no pessimista a {formatar(otim[ano], tipo)} no otimista. "
               f"O cenário {ctx['cenario']} tem {formatar(cen.loc[ano, col_kpi], tipo)}."))
with st.expander("Ver valores por ano"):
    tabela = pd.DataFrame({"Pessimista": pess, "Realista": q[0.5], "Otimista": otim, f"Cenário {ctx['cenario']}": cen[col_kpi]})
    st.dataframe(tabela.map(lambda v: formatar(v, tipo)).rename(index=lambda a: f"Ano {a}"), width="stretch")

# ---------------- 2. simulador ----------------
st.subheader(f"Simulador: e se? – cenário {ctx['cenario']}, Ano {ano}")
st.write("Mude a receita e os custos e veja o efeito no EBITDA, no lucro e nas margens. O cálculo refaz a DRE do ano "
         "com as variações escolhidas.")
c1, c2 = st.columns(2)
var_receita = c1.slider("Variação da receita (%)", -20, 20, 0, 1) / 100
var_custos = c2.slider("Variação dos custos (%)", -20, 20, 0, 1) / 100
with st.expander("Mais variáveis"):
    c1, c2, c3 = st.columns(3)
    var_dep = c1.slider("Depreciação e amortização (%)", -20, 20, 0, 1) / 100
    var_fin = c2.slider("Resultado financeiro (%)", -20, 20, 0, 1) / 100
    var_outros = c3.slider("Outros resultados operacionais (%)", -20, 20, 0, 1) / 100

original = lucro_simulado(linha)
simulado = lucro_simulado(linha, var_receita, var_custos, var_dep, var_fin, var_outros)
so_receita = lucro_simulado(linha, var_receita)
receita_custos = lucro_simulado(linha, var_receita, var_custos)

itens = [("A03 · Receita líquida", "receita_liquida", "rs"), ("A10 · EBITDA", "ebitda", "rs"),
         ("A13 · Lucro líquido", "lucro_liquido", "rs"), ("A11 · Margem EBITDA", "margem_ebitda", "pct"),
         ("A14 · Margem líquida", "margem_liquida", "pct"), ("C08 · Dívida líquida / EBITDA", "divida_liquida_ebitda", "x")]


def variacao(col, tipo):
    dif = simulado[col] - original[col]
    if abs(dif) < 1e-9:
        return None
    if tipo == "pct":
        return f"{delta_br(dif * 100, 1)} p.p. vs original"
    if tipo == "rs":
        return f"{delta_br(dif)} mi ({br(dif / original[col] * 100, 1)}%) vs original"
    return f"{delta_br(dif, 2)} vs original"


# na dívida líquida / EBITDA a cor fica neutra: com dívida líquida negativa, um EBITDA menor deixa o índice "melhor"
cartoes([(nome, formatar(simulado[col], t), variacao(col, t), f"Original: {formatar(original[col], t)}",
          None if col == "divida_liquida_ebitda" else col in MENOR_MELHOR) for nome, col, t in itens])

efeito_receita = so_receita["lucro_liquido"] - original["lucro_liquido"]
efeito_custos = receita_custos["lucro_liquido"] - so_receita["lucro_liquido"]
efeito_outros = simulado["lucro_liquido"] - receita_custos["lucro_liquido"]
fig = go.Figure(go.Waterfall(
    x=["Lucro original", "Efeito da receita", "Efeito dos custos", "Outras variáveis", "Lucro simulado"],
    measure=["absolute", "relative", "relative", "relative", "total"],
    y=[original["lucro_liquido"], efeito_receita, efeito_custos, efeito_outros, simulado["lucro_liquido"]],
    text=[formatar(v, "rs") for v in [original["lucro_liquido"], efeito_receita, efeito_custos, efeito_outros,
                                      simulado["lucro_liquido"]]],
    textposition="outside", increasing=dict(marker_color=VERDE), decreasing=dict(marker_color=VERMELHO),
    totals=dict(marker_color=AZUL), connector=dict(line=dict(color=CINZA))))
niveis = [original["lucro_liquido"], so_receita["lucro_liquido"], receita_custos["lucro_liquido"], simulado["lucro_liquido"]]
folga = max(max(niveis) - min(niveis), abs(original["lucro_liquido"]) * 0.05)
fig.update_yaxes(range=[min(niveis) - folga, max(niveis) + folga * 0.6])     # eixo aproximado para ver os efeitos
st.plotly_chart(layout(fig, "Do lucro original ao lucro simulado (eixo não começa no zero)", "R$ milhões", 420, "", False),
                width="stretch")
st.caption(md(f"Premissas: os tributos acompanham a receita, a alíquota efetiva de IR/CSLL do ano "
           f"({br(linha['aliquota_efetiva'] * 100, 1)}%) não muda e o caixa e a dívida ficam iguais."))

# ---------------- 3. o que mais mexe no lucro ----------------
st.subheader("O que mais mexe no lucro?")
st.write(f"Efeito no lucro líquido do Ano {ano} se cada item subir ou cair 10%, um de cada vez.")
testes = [("Receita líquida", "var_receita"), ("Custos", "var_custos"), ("Depreciação e amortização", "var_dep"),
          ("Resultado financeiro", "var_fin"), ("Outros resultados", "var_outros")]
linhas = []
for nome, arg in testes:
    sobe = lucro_simulado(linha, **{arg: 0.10})["lucro_liquido"] - original["lucro_liquido"]
    cai = lucro_simulado(linha, **{arg: -0.10})["lucro_liquido"] - original["lucro_liquido"]
    linhas.append({"item": nome, "sobe": sobe, "cai": cai})
tornado = pd.DataFrame(linhas).assign(tamanho=lambda t: t[["sobe", "cai"]].abs().max(axis=1)).sort_values("tamanho")
fig = go.Figure()
fig.add_trace(go.Bar(y=tornado["item"], x=tornado["sobe"], orientation="h", name="Item sobe 10%", marker_color=AZUL,
                     text=[formatar(v, "rs") for v in tornado["sobe"]], textposition="outside"))
fig.add_trace(go.Bar(y=tornado["item"], x=tornado["cai"], orientation="h", name="Item cai 10%", marker_color=LARANJA,
                     text=[formatar(v, "rs") for v in tornado["cai"]], textposition="outside"))
limite = tornado["tamanho"].max() * 1.45
fig.update_layout(barmode="overlay")
fig.update_xaxes(range=[-limite, limite], zeroline=True, zerolinecolor=CINZA)
st.plotly_chart(layout(fig, "Variação do lucro líquido com ±10% em cada item", "", 380, "Variação do lucro (R$ milhões)", False),
                width="stretch")
maior = tornado.iloc[-1]
st.caption(md(f"O item que mais mexe no lucro é **{maior['item'].lower()}**: 10% de variação mudam o lucro em cerca de "
           f"{formatar(maior['tamanho'], 'rs')}."))
