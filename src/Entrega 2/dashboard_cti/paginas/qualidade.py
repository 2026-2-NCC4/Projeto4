# paginas/qualidade.py - de onde vêm os dados, regras de qualidade e dicionário resumido (contribuição da Entrega 1)

import pandas as pd
import streamlit as st

from dados import COLUNAS_NECESSARIAS, DESCRICOES, regras_qualidade
from formatos import br, cabecalho

ctx = st.session_state["ctx"]
d = ctx["d"]

cabecalho("Qualidade dos dados", ctx, "De onde vêm os números do dashboard e quais conferências a base passa "
          "toda vez que o app abre.")

st.subheader("Caminho dos dados")
st.graphviz_chart("""
digraph {
  rankdir=LR; bgcolor="transparent";
  node [shape=box, style="rounded,filled", fillcolor="#eaf2fb", color="#2E5E8C", fontname="Helvetica", fontsize=11];
  edge [color="#8C8C8C"];
  bruto [label="Demonstrativo Fecap v3.csv\\n(dado bruto da CTI)"];
  prep [label="Preparacao_Dados_CTI.ipynb\\n(Entrega 1, Google Colab)"];
  base [label="base_cti_processada.csv\\n(LINHAS linhas)"];
  kpi [label="dados.py\\n(KPIs e conferências)"];
  dash [label="Dashboard\\n(7 páginas)", fillcolor="#eaf6ee", color="#1F6F4A"];
  bruto -> prep -> base -> kpi -> dash;
}
""".replace("LINHAS", br(len(d))), width="stretch")

c = st.columns(4)
c[0].metric("Linhas", br(len(d)))
c[1].metric("Colunas da base", br(ctx["n_colunas_base"]))
c[2].metric("Cenários", br(d["cenario"].nunique()))
c[3].metric("Anos", br(d["ano"].nunique()))

st.subheader("Regras de qualidade")
st.dataframe(regras_qualidade(d), hide_index=True, width="stretch")
st.caption("OK = a regra passou em todas as linhas. Atenção = situação conhecida e explicada nas notas metodológicas.")

st.subheader("Colunas usadas pelo dashboard")
dic = pd.DataFrame([{"Coluna": col, "Descrição": DESCRICOES.get(col, ""),
                     "Preenchido": f"{br(d[col].notna().mean() * 100, 1)}%",
                     "Mínimo": br(d[col].min(), 1) if pd.api.types.is_numeric_dtype(d[col]) else "–",
                     "Máximo": br(d[col].max(), 1) if pd.api.types.is_numeric_dtype(d[col]) else "–"}
                    for col in COLUNAS_NECESSARIAS])
st.dataframe(dic, hide_index=True, width="stretch", height=36 * (len(dic) + 1) + 4)
st.caption("Valores em R\\$ milhões, menos cenário e ano.")

cen = ctx["cen"].reset_index()
st.download_button("Baixar os dados do cenário escolhido (CSV)",
                   cen[["cenario", "ano"] + [c for c in COLUNAS_NECESSARIAS if c not in ("cenario", "ano")]]
                   .to_csv(sep=";", decimal=",", index=False).encode("utf-8-sig"),
                   file_name=f"dados_cenario_{ctx['cenario']}.csv", mime="text/csv")
