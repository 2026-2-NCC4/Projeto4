# dados.py
# Leitura da base, cálculo dos indicadores, regras de qualidade, regressão e simulação.
# PI Ciência de Dados - Entrega 2 - Dashboard CTI (FECAP)
# Integrantes: Bruno Nobrega, Kaio Inglez, Mauricio Suster e Yuri Santana

import os

import numpy as np
import pandas as pd
import streamlit as st

from formatos import br

# >>> DADOS: caminho da base final da Entrega 1 (saída do notebook Preparacao_Dados_CTI.ipynb).
#     Se a base mudar de nome ou de pasta, altere só esta linha.
ARQUIVO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados", "base_cti_processada.csv")

# colunas da base que o dashboard usa (valores em R$ milhões)
COLUNAS_NECESSARIAS = ["cenario", "ano", "grupo_cenario", "receita", "tributos", "custos", "depreciacao_amortizacao",
                       "resultado_operacional", "outros_resultados", "resultado_financeiro", "ir_cs", "lucro_liquido",
                       "caixa", "ativo_total", "divida_bruta", "patrimonio_liquido", "investimentos", "dividendos",
                       "geracao_caixa"]

# >>> KPIs principais (os 5 do dicionário que ficam na visão executiva):
#     (código, nome, coluna, tipo, fórmula). Tipos: rs = R$ milhões, pct = %, x = vezes.
KPIS = [
    ("A03", "Receita líquida", "receita_liquida", "rs", "Receita bruta − tributos sobre a receita"),
    ("A10", "EBITDA", "ebitda", "rs", "Receita líquida − custos + outros resultados operacionais"),
    ("A11", "Margem EBITDA", "margem_ebitda", "pct", "EBITDA / receita líquida"),
    ("A14", "Margem líquida", "margem_liquida", "pct", "Lucro líquido / receita líquida"),
    ("C08", "Dívida líquida / EBITDA", "divida_liquida_ebitda", "x", "(Dívida bruta − caixa) / EBITDA"),
]

# indicadores complementares (também do dicionário, ou de apoio quando não têm código)
COMPLEMENTARES = [
    ("A01", "Receita bruta", "receita", "rs", "DRE - Receita"),
    ("A04", "Custos", "custos", "rs", "DRE - Custos (sinal positivo)"),
    ("A13", "Lucro líquido", "lucro_liquido", "rs", "DRE - Resultado líquido"),
    ("C01", "Dívida bruta", "divida_bruta", "rs", "Empréstimos e financiamentos"),
    ("C03", "Endividamento geral", "endividamento_geral", "pct", "(Ativo total − patrimônio líquido) / ativo total"),
    ("–", "Payout", "payout", "pct", "Dividendos pagos / lucro líquido"),
    ("–", "Geração de caixa", "geracao_caixa", "rs", "Variação do caixa no ano"),
    ("–", "Caixa", "caixa", "rs", "Disponível no fim do ano"),
    ("–", "Dívida líquida", "divida_liquida", "rs", "Dívida bruta − caixa"),
    ("–", "Dividendos pagos", "dividendos", "rs", "Distribuição para os acionistas"),
    ("–", "Investimentos", "investimentos", "rs", "Investimentos pagos no ano"),
]
TODOS = KPIS + COMPLEMENTARES
MENOR_MELHOR = {"divida_liquida_ebitda", "endividamento_geral", "custos", "divida_bruta", "divida_liquida"}


@st.cache_data
def carregar_base(caminho=ARQUIVO):
    return pd.read_csv(caminho, sep=";", decimal=",")


def validar_colunas(base):
    """Lista as colunas que faltam na base (lista vazia = tudo certo)."""
    return [c for c in COLUNAS_NECESSARIAS if c not in base.columns]


@st.cache_data
def calcular_indicadores(base):
    """Calcula os KPIs a partir das colunas da base (mesmas fórmulas do dicionário de KPIs)."""
    d = base.copy()
    for col in ["receita_liquida", "ebitda", "margem_ebitda", "margem_liquida", "divida_liquida"]:   # guarda as colunas da Entrega 1
        if col in d.columns:
            d[f"{col}_e1"] = d[col]
    d["receita_liquida"] = d["receita"] - d["tributos"]
    d["ebitda"] = d["receita_liquida"] - d["custos"] + d["outros_resultados"]
    d["margem_ebitda"] = d["ebitda"] / d["receita_liquida"]
    d["margem_liquida"] = d["lucro_liquido"] / d["receita_liquida"]
    d["divida_liquida"] = d["divida_bruta"] - d["caixa"]
    d["divida_liquida_ebitda"] = d["divida_liquida"] / d["ebitda"]
    d["endividamento_geral"] = (d["ativo_total"] - d["patrimonio_liquido"]) / d["ativo_total"]
    d["payout"] = d["dividendos"] / d["lucro_liquido"]
    d["lair"] = d["lucro_liquido"] + d["ir_cs"]                       # lucro antes do IR/CSLL
    d["aliquota_efetiva"] = d["ir_cs"] / d["lair"]
    d["grupo2"] = (d["cenario"] > 1000).astype(int)
    return d


def regras_qualidade(d):
    """Regras de qualidade da Entrega 1 conferidas de novo no dashboard."""
    por_cenario = d.groupby("cenario")["ano"].nunique()
    vazios = d[COLUNAS_NECESSARIAS].isna().sum()
    anos_vazios = sorted(d.loc[d[COLUNAS_NECESSARIAS].isna().any(axis=1), "ano"].unique())
    anos_txt = lambda anos: ("Ano " if len(anos) == 1 else "Anos ") + ", ".join(map(str, anos))
    texto_vazios = (f"{br(vazios.sum())} células vazias em {', '.join(vazios[vazios > 0].index)} "
                    f"({anos_txt(anos_vazios)})") if vazios.sum() else "nenhuma célula vazia"
    acima = d["margem_ebitda"] > 1
    texto_margem = (f"{br(acima.sum())} linhas ({anos_txt(sorted(d.loc[acima, 'ano'].unique()))})"
                    if acima.any() else "nenhuma linha")
    regras = [
        ("Uma linha por cenário e ano", f"{d.duplicated(['cenario', 'ano']).sum()} linhas repetidas",
         d.duplicated(["cenario", "ano"]).sum() == 0),
        ("12 anos em todos os cenários", f"{(por_cenario != 12).sum()} cenários incompletos", (por_cenario == 12).all()),
    ]
    for col, nome, un in [("receita_liquida", "Receita líquida igual à da Entrega 1", " mi"),
                          ("ebitda", "EBITDA igual ao da Entrega 1", " mi"),
                          ("margem_ebitda", "Margem EBITDA igual à da Entrega 1", " p.p."),
                          ("margem_liquida", "Margem líquida igual à da Entrega 1", " p.p."),
                          ("divida_liquida", "Dívida líquida igual à da Entrega 1", " mi")]:
        if f"{col}_e1" in d.columns:
            dif = (d[col] - d[f"{col}_e1"]).abs().max() * (100 if un == " p.p." else 1)
            regras.append((nome, f"maior diferença: {br(dif, 4)}{un}", dif < 0.01))
    regras += [
        ("Resultado operacional = receita líquida − custos − depreciação",
         f"maior diferença: {br(abs(d['receita_liquida'] - d['custos'] - d['depreciacao_amortizacao'] - d['resultado_operacional']).max(), 4)} mi",
         abs(d["receita_liquida"] - d["custos"] - d["depreciacao_amortizacao"] - d["resultado_operacional"]).max() < 0.01),
        ("Lucro = operacional + outros + financeiro − IR/CSLL",
         f"maior diferença: {br(abs(d['resultado_operacional'] + d['outros_resultados'] + d['resultado_financeiro'] - d['ir_cs'] - d['lucro_liquido']).max(), 4)} mi",
         abs(d["resultado_operacional"] + d["outros_resultados"] + d["resultado_financeiro"] - d["ir_cs"] - d["lucro_liquido"]).max() < 0.01),
        ("Tributos entre 5% e 10% da receita",
         f"de {br(d['tributos'].div(d['receita']).min() * 100, 1)}% a {br(d['tributos'].div(d['receita']).max() * 100, 1)}%",
         d["tributos"].div(d["receita"]).between(0.05, 0.10).all()),
        ("Valores vazios", texto_vazios, None if vazios.sum() else True),
        ("Margem EBITDA acima de 100%", texto_margem, None if acima.any() else True),
    ]
    return pd.DataFrame([{"Regra": r, "Resultado": res, "Situação": "OK" if ok else ("Atenção" if ok is None else "Erro")}
                         for r, res, ok in regras])


def ols(d, y, xs):
    """Regressão linear por mínimos quadrados (numpy). Devolve coeficientes, IC 95%, R² e RMSE."""
    dados = d[[y] + xs].dropna()
    X = np.column_stack([np.ones(len(dados))] + [dados[x].to_numpy() for x in xs])
    Y = dados[y].to_numpy()
    beta, *_ = np.linalg.lstsq(X, Y, rcond=None)
    resid = Y - X @ beta
    n, k = X.shape
    sigma2 = resid @ resid / (n - k)
    ep = np.sqrt(np.diag(sigma2 * np.linalg.inv(X.T @ X)))
    r2 = 1 - (resid @ resid) / ((Y - Y.mean()) @ (Y - Y.mean()))
    tabela = pd.DataFrame({"coef": beta, "ep": ep, "ic_min": beta - 1.96 * ep, "ic_max": beta + 1.96 * ep},
                          index=["Intercepto"] + xs)
    return tabela, r2, np.sqrt(sigma2), n


def lucro_simulado(linha, var_receita=0.0, var_custos=0.0, var_dep=0.0, var_fin=0.0, var_outros=0.0):
    """Recalcula EBITDA e lucro de uma linha (cenário e ano) com variações em %.
    Premissas: os tributos acompanham a receita, a alíquota efetiva de IR/CSLL é a do próprio ano
    e não há IR/CSLL quando o resultado antes do imposto fica negativo."""
    rl = linha["receita_liquida"] * (1 + var_receita)
    custos = linha["custos"] * (1 + var_custos)
    dep = linha["depreciacao_amortizacao"] * (1 + var_dep)
    outros = linha["outros_resultados"] * (1 + var_outros)
    fin = linha["resultado_financeiro"] * (1 + var_fin)
    ebitda = rl - custos + outros
    lair = ebitda - dep + fin
    lucro = lair * (1 - linha["aliquota_efetiva"]) if lair > 0 else lair
    divida_liq = linha["divida_bruta"] - linha["caixa"]
    return {"receita_liquida": rl, "custos": custos, "ebitda": ebitda, "margem_ebitda": ebitda / rl,
            "lucro_liquido": lucro, "margem_liquida": lucro / rl, "divida_liquida_ebitda": divida_liq / ebitda}


# descrição das colunas da base (dicionário de dados resumido da Entrega 1)
DESCRICOES = {
    "cenario": "Número do cenário (1 a 1.200)", "ano": "Ano da concessão (1 a 12)",
    "grupo_cenario": "Grupo do cenário (1-1000 ou 1001-1200)", "receita": "DRE - Receita (bruta)",
    "tributos": "DRE - Tributos sobre a receita", "custos": "DRE - Custos",
    "depreciacao_amortizacao": "DRE - Depreciação e amortização", "resultado_operacional": "DRE - Resultado operacional",
    "outros_resultados": "DRE - Outros resultados operacionais", "resultado_financeiro": "DRE - Resultado financeiro",
    "ir_cs": "DRE - IR e CSLL", "lucro_liquido": "DRE - Resultado líquido", "caixa": "BAL - Disponível",
    "ativo_total": "BAL - Total do ativo", "divida_bruta": "BAL - Empréstimos e financiamentos",
    "patrimonio_liquido": "BAL - Patrimônio líquido", "investimentos": "FLU - Investimentos",
    "dividendos": "FLU - Distribuição para acionistas", "geracao_caixa": "FLU - Geração de caixa",
}
