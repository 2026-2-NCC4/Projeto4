# app.py
# Painel Financeiro - CTI Global
# Contabilidade e Finanças - Entrega 02 - Projeto Interdisciplinar 4º CCOMP (FECAP)
# Professor: Mauricio Lopes da Cunha
# Integrantes: Bruno Nobrega, Kaio Inglez, Mauricio Suster e Yuri Santana
#
# Conteúdo da pré-entrega de 30/10: 8 Índices da DFC, 9 Índices de capital de giro,
# 10 Fluxo de caixa e 11 DVA, junto com os KPIs.
# Para rodar:  python -m streamlit run app.py

import os
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from calculos import (carregar_dados, KPIS_E1, KPIS_E2, INDICES_DFC, CAPITAL_GIRO, FLEURIET,
                      linhas_dfc, linhas_indireto, linhas_dva)

st.set_page_config(page_title="Painel Financeiro - CTI", page_icon="📊", layout="wide")

VERDE, AZUL, LARANJA, CINZA, VERMELHO, ROXO = "#1F6F4A", "#2E5E8C", "#E07B39", "#8C8C8C", "#C0392B", "#7B4F9E"
ANOS = list(range(1, 13))


# ---------------- formatação em português ----------------
def br(v, casas=0):
    return f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")

def vazio(v):
    return v is None or (isinstance(v, float) and pd.isna(v))

def formatar(v, tipo):
    if vazio(v):
        return "n/a"
    if tipo == "txt":
        return str(v)
    texto = {"rs": lambda x: f"{'−' if x < 0 else ''}R$ {br(abs(x))} mi", "pct": lambda x: f"{br(x * 100, 1)}%",
             "x": lambda x: f"{br(x, 2)}x", "dias": lambda x: f"{br(x, 1)} dias", "anos": lambda x: f"{br(x, 2)} anos"}[tipo](v)
    return texto.replace("-", "−")

def layout_grafico(fig, titulo, eixo_y, barras=None):
    fig.update_layout(title=titulo, xaxis_title="Ano da concessão", yaxis_title=eixo_y, barmode=barras,
                      separators=",.", hovermode="x unified", height=430,
                      margin=dict(l=10, r=10, t=50, b=10), legend=dict(orientation="h", y=-0.2, yanchor="top", x=0))
    fig.update_xaxes(tickmode="linear", dtick=1)
    if eixo_y == "R$ milhões":
        fig.update_yaxes(tickformat=",.0f")
    return fig

def tabela_anos(cen, itens):
    """Tabela com um indicador por linha e os 12 anos nas colunas (igual à planilha)."""
    curto = lambda v, col, tipo: str(v).split(" - ")[0] if col == "tipo_fleuriet" and not vazio(v) else formatar(v, tipo)
    texto = pd.DataFrame({f"Ano {a}": [curto(cen.loc[a, col], col, tipo) for _, col, tipo in itens] for a in ANOS},
                         index=[nome for nome, _, _ in itens])
    numeros = pd.DataFrame({f"Ano {a}": [cen.loc[a, col] for _, col, _ in itens] for a in ANOS},
                           index=[nome for nome, _, _ in itens])
    return texto, numeros

def mostrar_tabela(texto, altura=None):
    """Tabela ano a ano com a coluna dos nomes mais larga."""
    st.dataframe(texto, width="stretch", height=altura or "auto",
                 column_config={"_index": st.column_config.TextColumn("Indicador", width="large")})

def grade(quantidade, por_linha=4):
    """Colunas para os cartões, no máximo 4 por linha para os valores não ficarem cortados."""
    colunas = []
    while len(colunas) < quantidade:
        colunas += st.columns(por_linha)
    return colunas

def baixar(numeros, nome_arquivo, rotulo="Baixar tabela (CSV)"):
    st.download_button(rotulo, numeros.to_csv(sep=";", decimal=",").encode("utf-8-sig"),
                       file_name=nome_arquivo, mime="text/csv", key=nome_arquivo)

def tabela_demonstrativo(linhas):
    """Tabela de demonstrativo (DFC ou DVA): totais em negrito com marcador."""
    return pd.DataFrame([{"Linha": ("▸ " + nome) if total else ("    " + nome), "R$ milhões": valor_tabela(valor)}
                         for nome, valor, total in linhas])

def valor_tabela(v):
    return "n/a" if vazio(v) else ("−" if v < 0 else "") + br(abs(v))


# ---------------- dados ----------------
ARQUIVO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados", "dados_painel.csv")

if not os.path.exists(ARQUIVO):
    st.error("Arquivo dados/dados_painel.csv não encontrado. Rode antes: python preparar_dados.py")
    st.stop()

@st.cache_data
def ler_dados():
    return carregar_dados(ARQUIVO)

todos = ler_dados()
mediana = todos.groupby("ano").median(numeric_only=True)


# ---------------- barra lateral ----------------
st.sidebar.title("Painel Financeiro")
st.sidebar.caption("CTI Global · PI 4º CCOMP FECAP")
st.sidebar.header("Filtros")
cenario = int(st.sidebar.number_input("Cenário (1 a 1.200)", min_value=1, max_value=1200, value=1, step=1))
ano = st.sidebar.slider("Ano", 1, 12, 1)
comparar = st.sidebar.checkbox("Mostrar mediana dos 1.200 cenários nos gráficos", value=True)
st.sidebar.caption("O cenário 1 é o mesmo da planilha da Entrega 2.")

cen = todos[todos["cenario"] == cenario].set_index("ano")
linha = cen.loc[ano]
anterior = cen.loc[ano - 1] if ano > 1 else None
ano_todos = todos[todos["ano"] == ano]

st.title("Painel Financeiro – CTI Global")
st.caption(f"Cenário {cenario} de 1.200 · Ano {ano} de 12 · valores em R\\$ milhões")


def card(coluna, titulo, chave, tipo, ajuda="", cor="normal"):
    """Cartão com o valor do ano e a variação em relação ao ano anterior."""
    valor = linha[chave]
    delta = None
    if chave == "tipo_fleuriet" and not vazio(valor):        # "Tipo 1 - Excelente" -> título "... Tipo 1", valor "Excelente"
        numero, nome = str(valor).split(" - ")
        titulo, valor = f"{titulo} · {numero}", nome
    if tipo != "txt" and anterior is not None and not vazio(valor) and not vazio(anterior[chave]):
        if tipo == "rs":
            delta = f"{br(valor - anterior[chave])} mi vs ano anterior"
        elif tipo == "pct":
            delta = f"{br((valor - anterior[chave]) * 100, 1)} p.p. vs ano anterior"
        else:
            delta = f"{br(valor - anterior[chave], 2)} vs ano anterior"
    coluna.metric(titulo, formatar(valor, tipo), delta, help=ajuda, delta_color=cor)

def linha_mediana(fig, coluna, nome, cor, escala=1):
    if comparar:
        fig.add_trace(go.Scatter(x=ANOS, y=mediana[coluna] * escala, name=f"{nome} (mediana)", showlegend=False,
                                 mode="lines", line=dict(color=cor, width=1.5, dash="dash")))


# nomes curtos para caber nos cartões (o nome completo aparece no "?")
CURTOS = {"H01": "FCO", "H04": "Cobertura da dívida", "H05": "NCG", "H08": "Fleuriet",
          "H09": "Valor adicionado", "H10": "VA p/ acionistas", "H11": "VA p/ governo"}

CURTOS_DFC = {"cobertura_juros_caixa": "Cobertura de juros", "cobertura_servico_divida": "Cobertura da dívida",
              "retorno_caixa_ativo": "Retorno de caixa s/ ativo", "retorno_caixa_pl": "Retorno de caixa s/ PL",
              "capacidade_investimento": "Capacidade de investimento", "anos_pagar_divida": "Anos p/ pagar a dívida"}

aba_kpis, aba8, aba9, aba10, aba11, aba_notas = st.tabs(
    ["KPIs", "8 · Índices da DFC", "9 · Capital de giro", "10 · Fluxo de caixa", "11 · DVA", "Notas"])


# ---------------- KPIs ----------------
with aba_kpis:
    st.subheader("KPIs da Entrega 1")
    colunas = grade(len(KPIS_E1))
    for i, (codigo, nome, col, tipo, formula) in enumerate(KPIS_E1):
        menor_melhor = col in ("divida_liquida_ebitda", "endividamento_geral")
        card(colunas[i], f"{codigo} · {nome}", col, tipo, formula, "inverse" if menor_melhor else "normal")

    st.subheader("KPIs novos da Entrega 2")
    colunas = grade(len(KPIS_E2))
    for i, (codigo, nome, col, tipo, formula) in enumerate(KPIS_E2):
        cor = "off" if col in ("ncg", "saldo_tesouraria", "ciclo_financeiro", "pct_governo") else "normal"
        card(colunas[i], f"{codigo} · {CURTOS.get(codigo, nome)}", col, tipo, f"{nome}: {formula}", cor)
    if ano == 12:
        st.info("No Ano 12 o arquivo não traz o balanço completo, por isso liquidez, endividamento e capital de giro ficam n/a.")

    st.subheader(f"KPIs ano a ano – cenário {cenario}")
    itens = [(f"{c} {n}", col, t) for c, n, col, t, _ in KPIS_E1 + KPIS_E2]
    texto, numeros = tabela_anos(cen, itens)
    mostrar_tabela(texto, 670)
    baixar(numeros, f"kpis_cenario_{cenario}.csv")
    st.caption("Os valores do cenário 1 são os mesmos da aba KPIs da Planilha_Entrega02_Contabilidade_CTI.xlsx.")


# ---------------- 8. índices da DFC ----------------
with aba8:
    st.write("Índices calculados com o **fluxo de caixa operacional (FCO)**: mostram se o caixa da operação "
             "paga juros, dívida, dividendos e investimentos.")
    colunas = grade(len(INDICES_DFC))
    for i, (nome, col, tipo, formula, leitura) in enumerate(INDICES_DFC):
        card(colunas[i], CURTOS_DFC.get(col, nome), col, tipo, f"{nome}: {formula}. {leitura}.",
             "inverse" if col == "anos_pagar_divida" else "normal")

    col1, col2 = st.columns(2)
    fig = go.Figure()
    for col, nome, cor in [("cobertura_servico_divida", "Cobertura do serviço da dívida", AZUL),
                           ("qualidade_resultado", "Qualidade do resultado", VERDE),
                           ("cobertura_dividendos", "Cobertura de dividendos", LARANJA)]:
        fig.add_trace(go.Scatter(x=ANOS, y=cen[col], name=nome, mode="lines+markers", line=dict(color=cor, width=3)))
        linha_mediana(fig, col, nome, cor)
    fig.add_hline(y=1, line_dash="dot", line_color=VERMELHO, annotation_text="1x", annotation_position="bottom right")
    fig.update_yaxes(type="log", tickvals=[0.5, 1, 2, 5, 10, 20, 50], ticktext=["0,5", "1", "2", "5", "10", "20", "50"])
    col1.plotly_chart(layout_grafico(fig, "Coberturas com o caixa da operação (escala log)", "vezes"), width="stretch")

    fig = go.Figure()
    fig.add_trace(go.Bar(x=ANOS, y=cen["fco"], name="FCO", marker_color=VERDE))
    fig.add_trace(go.Bar(x=ANOS, y=-cen["dividendos_pagos"], name="Dividendos pagos", marker_color=LARANJA))
    fig.add_trace(go.Bar(x=ANOS, y=-cen["juros_amortizacao_pagos"], name="Juros e amortização", marker_color=AZUL))
    fig.add_trace(go.Bar(x=ANOS, y=-cen["fci"], name="Investimentos", marker_color=CINZA))
    col2.plotly_chart(layout_grafico(fig, "Quanto a operação gera e para onde vai o caixa", "R$ milhões", "group"),
                      width="stretch")

    st.subheader(f"Nos 1.200 cenários – Ano {ano}")
    c = st.columns(4)
    c[0].metric("Qualidade do resultado > 1", formatar((ano_todos["qualidade_resultado"] > 1).mean(), "pct"),
                help="% dos cenários em que o FCO é maior que o lucro líquido")
    c[1].metric("Serviço da dívida coberto (> 1x)", formatar((ano_todos["cobertura_servico_divida"] > 1).mean(), "pct"),
                help="% dos cenários em que o FCO paga juros + amortização do ano")
    c[2].metric("Dividendos cobertos (> 1x)", formatar((ano_todos["cobertura_dividendos"] > 1).mean(), "pct"),
                help="% dos cenários em que o FCO é maior que os dividendos pagos")
    c[3].metric("Mediana da margem de caixa", formatar(ano_todos["margem_caixa"].median(), "pct"))

    texto, numeros = tabela_anos(cen, [(n, c_, t) for n, c_, t, _, _ in INDICES_DFC])
    with st.expander("Ver tabela ano a ano", expanded=True):
        mostrar_tabela(texto)
    baixar(numeros, f"indices_dfc_cenario_{cenario}.csv")


# ---------------- 9. capital de giro ----------------
with aba9:
    st.write("Modelo dinâmico de **Fleuriet**: o balanço é separado em contas financeiras (caixa e dívida) e "
             "contas cíclicas (da operação).")
    if ano == 12:
        st.info("No Ano 12 o arquivo não traz o balanço completo, então os índices de capital de giro ficam n/a. "
                "Escolha um ano de 1 a 11.")
    c = grade(6, 3)
    card(c[0], "NCG", "ncg", "rs", "Necessidade de capital de giro = ACC − PCC", "off")
    card(c[1], "Saldo de tesouraria", "saldo_tesouraria", "rs", "ST = ACF − PCF", "off")
    card(c[2], "Capital de giro (CDG)", "cdg", "rs", "PL + exigível LP − realizável LP − permanente", "off")
    card(c[3], "CCL", "ccl", "rs", "Capital circulante líquido = NCG + ST", "off")
    card(c[4], "Ciclo financeiro", "ciclo_financeiro", "dias", "PME + PMR − PMP", "inverse")
    card(c[5], "Fleuriet", "tipo_fleuriet", "txt", "Tipo pela combinação de sinais de CDG, NCG e ST")

    col1, col2 = st.columns(2)
    fig = go.Figure()
    for col, nome, cor in [("ncg", "NCG", LARANJA), ("cdg", "CDG", AZUL), ("saldo_tesouraria", "Saldo de tesouraria", VERDE)]:
        fig.add_trace(go.Scatter(x=ANOS, y=cen[col], name=nome, mode="lines+markers", line=dict(color=cor, width=3)))
        linha_mediana(fig, col, nome, cor)
    fig.add_hline(y=0, line_color=CINZA)
    col1.plotly_chart(layout_grafico(fig, "NCG, CDG e saldo de tesouraria", "R$ milhões"), width="stretch")

    fig = go.Figure()
    for col, nome, cor in [("pmr", "PMR", AZUL), ("pmp", "PMP", LARANJA), ("pme", "PME", CINZA),
                           ("ciclo_financeiro", "Ciclo financeiro", ROXO)]:
        fig.add_trace(go.Scatter(x=ANOS, y=cen[col], name=nome, mode="lines+markers", line=dict(color=cor, width=3)))
    fig.add_hline(y=0, line_color=CINZA)
    col2.plotly_chart(layout_grafico(fig, "Prazos médios e ciclo financeiro", "dias"), width="stretch")

    col1, col2 = st.container(), st.container()
    with col1:
        st.subheader(f"Tipo Fleuriet nos 1.200 cenários – Ano {ano}")
        contagem = ano_todos["tipo_fleuriet"].value_counts().reindex(FLEURIET["Tipo"]).fillna(0)
        if contagem.sum() == 0:
            st.write("n/a no Ano 12.")
        else:
            fig = go.Figure(go.Bar(x=contagem.values / contagem.sum() * 100, y=contagem.index, orientation="h",
                                   marker_color=AZUL, text=[f"{br(v / contagem.sum() * 100, 1)}%" for v in contagem.values],
                                   textposition="outside"))
            fig.update_layout(xaxis_title="% dos cenários", height=280, separators=",.", xaxis_range=[0, 125],
                              margin=dict(l=10, r=40, t=10, b=10), yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig, width="stretch")
    with col2:
        st.subheader("Os 6 tipos do modelo Fleuriet")
        ref = FLEURIET.copy()
        ref.insert(0, "Cenário", ["◀ atual" if t == linha["tipo_fleuriet"] else "" for t in ref["Tipo"]])
        st.dataframe(ref, hide_index=True, width="stretch",
                     column_config={"Leitura": st.column_config.TextColumn(width="large")})

    itens = [(n, c_, t) for n, c_, t, _ in CAPITAL_GIRO] + [("Estrutura (Fleuriet)", "tipo_fleuriet", "txt")]
    texto, numeros = tabela_anos(cen, itens)
    with st.expander("Ver tabela ano a ano", expanded=True):
        mostrar_tabela(texto, 530)
    baixar(numeros, f"capital_de_giro_cenario_{cenario}.csv")


# ---------------- 10. fluxo de caixa ----------------
with aba10:
    st.write("Demonstração do fluxo de caixa (CPC 03) pelo **método direto**, separada em operação, "
             "investimento e financiamento.")
    c = grade(5, 3)
    card(c[0], "FCO (operação)", "fco", "rs", "Recebimentos − pagamentos da operação")
    card(c[1], "FCI (investimento)", "fci", "rs", "Investimentos pagos", "off")
    card(c[2], "FCF (financiamento)", "fcf", "rs", "Juros e amortização + dividendos pagos", "off")
    card(c[3], "Variação do caixa", "variacao_caixa", "rs", "FCO + FCI + FCF", "off")
    card(c[4], "Saldo final de caixa", "saldo_final", "rs", "Saldo inicial + variação do caixa", "off")

    fig = go.Figure()
    fig.add_trace(go.Bar(x=ANOS, y=cen["fco"], name="FCO", marker_color=VERDE))
    fig.add_trace(go.Bar(x=ANOS, y=cen["fci"], name="FCI", marker_color=CINZA))
    fig.add_trace(go.Bar(x=ANOS, y=cen["fcf"], name="FCF", marker_color=LARANJA))
    fig.add_trace(go.Scatter(x=ANOS, y=cen["saldo_final"], name="Saldo final de caixa", mode="lines+markers",
                             line=dict(color=AZUL, width=3)))
    st.plotly_chart(layout_grafico(fig, f"Fluxo de caixa por atividade – cenário {cenario}", "R$ milhões", "relative"),
                    width="stretch")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"Método direto – Ano {ano}")
        st.dataframe(tabela_demonstrativo(linhas_dfc(linha)), hide_index=True, width="stretch", height=530)
        dif = linha["conf_saldo_final"]
        st.success(f"Conferência: o saldo final bate com o caixa do balanço (diferença de R\\$ {br(abs(dif), 6)} mi).")
    with col2:
        st.subheader(f"Método indireto – Ano {ano}")
        if 2 <= ano <= 11:
            st.dataframe(tabela_demonstrativo(linhas_indireto(linha)), hide_index=True, width="stretch", height=390)
            st.caption(f"\"Outros ajustes\" é a parte do FCO que as contas do balanço não explicam: "
                       f"{br(abs(linha['outros_ajustes']) / linha['fco'] * 100, 1)}% do FCO neste ano.")
        else:
            st.info("O método indireto precisa do balanço do ano anterior e do ano atual, por isso só aparece nos Anos 2 a 11.")

    itens = [("Recebimentos de clientes", "recebimentos_clientes", "rs"), ("Tributos pagos", "tributos_pagos", "rs"),
             ("Custos pagos", "custos_pagos", "rs"), ("IR e CSLL pagos", "ir_cs_pagos", "rs"),
             ("Receitas financeiras recebidas", "receitas_financeiras_recebidas", "rs"), ("FCO", "fco", "rs"),
             ("FCI (investimentos)", "fci", "rs"), ("Juros e amortização pagos", "juros_amortizacao_pagos", "rs"),
             ("Dividendos pagos", "dividendos_pagos", "rs"), ("FCF", "fcf", "rs"), ("Variação do caixa", "variacao_caixa", "rs"),
             ("Saldo inicial", "saldo_inicial", "rs"), ("Saldo final", "saldo_final", "rs")]
    texto, numeros = tabela_anos(cen, itens)
    with st.expander("Ver DFC dos 12 anos"):
        mostrar_tabela(texto, 480)
    baixar(numeros, f"fluxo_de_caixa_cenario_{cenario}.csv", "Baixar DFC (CSV)")


# ---------------- 11. DVA ----------------
with aba11:
    st.write("Demonstração do valor adicionado (CPC 09): quanto de riqueza a concessão gera e com quem ela é dividida.")
    c = st.columns(5)
    card(c[0], "Valor adicionado total", "va_total", "rs", "Valor adicionado líquido + recebido em transferência")
    card(c[1], "Valor adicionado / receita", "va_sobre_receita", "pct", "Valor adicionado total / receita bruta")
    card(c[2], "Para o governo", "pct_governo", "pct", "(Tributos + IR/CSLL) / valor adicionado total", "off")
    card(c[3], "Para terceiros (juros)", "pct_terceiros", "pct", "Juros / valor adicionado total", "off")
    card(c[4], "Para os acionistas", "pct_acionistas", "pct", "Lucro líquido / valor adicionado total", "off")

    geracao, distribuicao = linhas_dva(linha)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"Geração do valor adicionado – Ano {ano}")
        st.dataframe(tabela_demonstrativo(geracao), hide_index=True, width="stretch")
    with col2:
        st.subheader(f"Distribuição – Ano {ano}")
        st.dataframe(pd.DataFrame([{"Para quem": n, "R$ milhões": valor_tabela(v), "%": formatar(p, "pct")}
                                   for n, v, p in distribuicao]), hide_index=True, width="stretch")
        st.success(f"Conferência: valor adicionado total = total distribuído (diferença de R\\$ {br(abs(linha['conf_dva']), 6)} mi).")

    fig = go.Figure()
    for col, nome, cor in [("pct_governo", "Governo", AZUL), ("pct_terceiros", "Terceiros (juros)", CINZA),
                           ("pct_acionistas", "Acionistas", VERDE)]:
        fig.add_trace(go.Bar(x=ANOS, y=cen[col] * 100, name=nome, marker_color=cor))
    st.plotly_chart(layout_grafico(fig, f"Com quem o valor adicionado é dividido – cenário {cenario}", "% do valor adicionado",
                                   "stack"), width="stretch")
    st.caption("A DVA não tem a linha de pessoal: o arquivo da CTI não separa salários, eles ficam dentro dos custos (insumos).")

    itens = [("Receita bruta", "receita_bruta", "rs"), ("Outras receitas operacionais", "outras_receitas", "rs"),
             ("Insumos (custos)", "insumos", "rs"), ("Valor adicionado bruto", "va_bruto", "rs"),
             ("Depreciação e amortização", "depreciacao", "rs"), ("Valor adicionado líquido", "va_liquido", "rs"),
             ("Recebido em transferência", "va_transferencia", "rs"), ("Valor adicionado total", "va_total", "rs"),
             ("Governo", "dist_impostos", "rs"), ("Terceiros (juros)", "dist_terceiros", "rs"),
             ("Acionistas", "dist_acionistas", "rs"), ("% governo", "pct_governo", "pct"),
             ("% terceiros", "pct_terceiros", "pct"), ("% acionistas", "pct_acionistas", "pct"),
             ("Valor adicionado / receita", "va_sobre_receita", "pct")]
    texto, numeros = tabela_anos(cen, itens)
    with st.expander("Ver DVA dos 12 anos"):
        mostrar_tabela(texto, 560)
    baixar(numeros, f"dva_cenario_{cenario}.csv", "Baixar DVA (CSV)")


# ---------------- notas ----------------
with aba_notas:
    st.markdown("""
**Fonte:** arquivo *Demonstrativo Fecap v3.csv* enviado pela CTI Global (balanço, DRE e fluxo de caixa de uma
concessionária, 12 anos × 1.200 cenários simulados).

**Como os números foram feitos:** o script *calculo_entrega2.py* calcula tudo para os 1.200 cenários e o
*preparar_dados.py* gera o arquivo que o painel lê. O cenário 1 é igual à *Planilha_Entrega02_Contabilidade_CTI.xlsx*
(abas 8_Indices_DFC, 9_Capital_de_Giro, 10_Fluxo_de_Caixa, 11_DVA e KPIs), e o *testar_painel.py* confere isso.

**Unidades:** R\\$ milhões nominais; prazos em dias (ano de 360 dias); índices em vezes (x) ou em %.
""")
    st.subheader("Fórmulas")
    formulas = pd.DataFrame(
        [{"Grupo": "KPIs", "Indicador": f"{c} {n}", "Fórmula": f} for c, n, _, _, f in KPIS_E1 + KPIS_E2] +
        [{"Grupo": "8 · Índices da DFC", "Indicador": n, "Fórmula": f} for n, _, _, f, _ in INDICES_DFC] +
        [{"Grupo": "9 · Capital de giro", "Indicador": n, "Fórmula": f} for n, _, _, f in CAPITAL_GIRO] +
        [{"Grupo": "10 · Fluxo de caixa", "Indicador": "FCO", "Fórmula": "Receita + tributos + custos + IR/CSLL + receitas financeiras (linhas FLU)"},
         {"Grupo": "10 · Fluxo de caixa", "Indicador": "FCI", "Fórmula": "FLU - Investimentos"},
         {"Grupo": "10 · Fluxo de caixa", "Indicador": "FCF", "Fórmula": "FLU - Despesas financeiras (juros + amortização) + dividendos"},
         {"Grupo": "11 · DVA", "Indicador": "Valor adicionado total", "Fórmula": "Receita + outras receitas − insumos − depreciação + receitas financeiras"},
         {"Grupo": "11 · DVA", "Indicador": "Distribuição", "Fórmula": "Governo (tributos + IR/CSLL) + terceiros (juros) + acionistas (lucro)"}])
    st.dataframe(formulas, hide_index=True, width="stretch", height=560)

    st.subheader("Conferências (todos os 1.200 cenários)")
    conf = pd.DataFrame([
        {"Conferência": "Saldo final da DFC = caixa do balanço", "Maior diferença (R$ mi)": todos["conf_saldo_final"].abs().max()},
        {"Conferência": "FCO + FCI + FCF = geração de caixa do arquivo", "Maior diferença (R$ mi)": todos["conf_geracao"].abs().max()},
        {"Conferência": "Valor adicionado = total distribuído", "Maior diferença (R$ mi)": todos["conf_dva"].abs().max()},
        {"Conferência": "CCL = NCG + saldo de tesouraria", "Maior diferença (R$ mi)": todos["conf_capital_giro"].abs().max()},
    ])
    conf["Maior diferença (R$ mi)"] = conf["Maior diferença (R$ mi)"].map(lambda v: br(v, 6))
    st.dataframe(conf, hide_index=True, width="stretch")

    st.markdown("""
**Limitações:**
- O arquivo junta juros e amortização da dívida numa linha só, então os dois ficam no financiamento.
- A DVA não tem a linha de pessoal, porque os salários estão dentro dos custos.
- No Ano 12 não há balanço completo: liquidez, endividamento e capital de giro ficam n/a.
- O passivo circulante financeiro (PCF) foi estimado como a parte da dívida que vence no ano seguinte.
- Os prazos médios usam saldos finais e os custos no lugar das compras.
- No método indireto sobra uma parte pequena do FCO sem explicação pelas contas do balanço ("outros ajustes").
""")
