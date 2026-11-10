# formatos.py
# Formatação de números no padrão brasileiro, cores e layout padrão dos gráficos.

import re

import pandas as pd
import streamlit as st

VERDE, AZUL, LARANJA, CINZA, VERMELHO, ROXO = "#1F6F4A", "#2E5E8C", "#E07B39", "#8C8C8C", "#C0392B", "#7B4F9E"
UNIDADE = {"rs": "R$ milhões", "pct": "%", "x": "vezes"}


def br(v, casas=0):
    """Número no padrão brasileiro (1.234,5), com sinal de menos tipográfico."""
    texto = f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return texto.replace("-", "−")


def formatar(v, tipo):
    if v is None or pd.isna(v):
        return "n/a"
    if tipo == "rs":
        return f"{'−' if v < 0 else ''}R$ {br(abs(v))} mi"
    if tipo == "pct":
        return f"{br(v * 100, 1)}%"
    return f"{br(v, 2)}x"


def delta_br(v, casas=0):
    """Número para o delta dos cartões: o sinal de menos fica ASCII ("-"), porque é por ele que o
    Streamlit decide se a seta aponta para cima ou para baixo."""
    return br(v, casas).replace("−", "-")


def diferenca(v, ref, tipo, texto="vs mediana"):
    """Texto do delta dos cartões (diferença para uma referência). None quando a diferença é zero."""
    if pd.isna(v) or pd.isna(ref):
        return None
    dif, casas, sufixo = {"pct": ((v - ref) * 100, 1, " p.p."), "rs": (v - ref, 0, " mi")}.get(tipo, (v - ref, 2, ""))
    if round(dif, casas) == 0:
        return None
    return f"{delta_br(dif, casas)}{sufixo} {texto}"


def escala(tipo):
    """Nos gráficos, % aparece multiplicado por 100."""
    return 100 if tipo == "pct" else 1


def layout(fig, titulo, eixo_y, altura=420, eixo_x="Ano da concessão", anos=True):
    fig.update_layout(title=titulo, xaxis_title=eixo_x, yaxis_title=eixo_y, separators=",.", height=altura,
                      hovermode="x unified" if anos else "closest", margin=dict(l=10, r=10, t=60, b=10),
                      legend=dict(orientation="h", y=-0.22, yanchor="top", x=0, title_text=""))
    if anos:
        fig.update_xaxes(dtick=1)
    if "R$" in eixo_y:                     # 10.000 em vez de 10k
        fig.update_yaxes(tickformat=",.0f")
    if "R$" in eixo_x:
        fig.update_xaxes(tickformat=",.0f")
    return fig


def cartoes(itens, por_linha=3):
    """Desenha cartões st.metric, no máximo 3 por linha para os valores não ficarem cortados.
    itens = lista de (rótulo, valor formatado, delta, ajuda, menor_melhor), menor_melhor = True, False ou None."""
    colunas = []
    while len(colunas) < len(itens):
        colunas += st.columns(por_linha)
    for coluna, (rotulo, valor, delta, ajuda, menor_melhor) in zip(colunas, itens):
        cor = "off" if menor_melhor is None else ("inverse" if menor_melhor else "normal")   # None = sem lado melhor
        coluna.metric(rotulo, valor, delta, help=ajuda, delta_color=cor)


def cabecalho(titulo, ctx, texto=None):
    """Título da página com a linha de contexto (filtros, unidade, fonte e data)."""
    st.title(titulo)
    st.caption(f"Cenário {ctx['cenario']} · {ctx['grupo']} · Anos {ctx['ano_ini']} a {ctx['ano_fim']} · "
               f"ano de referência {ctx['ano_ref']} · R\\$ milhões nominais · fonte: CTI Global · "
               f"atualizado em {ctx['atualizado']}")
    if texto:
        st.write(texto)
    if ctx["ano_ref"] == 12:
        st.info("O Ano 12 é atípico (fim da concessão): a dívida é zerada, os dividendos sobem muito e a margem "
                "EBITDA passa de 100%. Para comparar com os outros anos, use o Ano 11.")


def md(texto):
    """Escapa o $ de "R$" para o Markdown do Streamlit não ler o trecho como fórmula matemática."""
    return re.sub(r"(?<!\\)\$", r"\\$", texto)
