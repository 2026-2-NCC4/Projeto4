# calculo_kpis.py
# Contabilidade e Finanças - Entrega 01 - Projeto Interdisciplinar CTI (FECAP)
# Professor: Mauricio Lopes da Cunha
# Integrantes: Bruno Nobrega, Kaio Inglez, Mauricio Suster e Yuri Santana
#
# Calcula os KPIs do dicionário para todos os cenários e anos.
# Uso: python calculo_kpis.py "Demonstrativo Fecap v3.csv"
# Saídas: kpis_todos_cenarios.csv e kpis_cenario_base.csv (usado na aba Validacao da planilha)

import sys
import numpy as np
import pandas as pd

# ---------------- premissas (iguais às da aba Premissas da planilha) ----------------
PCT_CUSTO_VARIAVEL = 0.30
ALIQUOTA = 0.34
KE = 0.10 + 0.80 * 0.06          # Rf + beta x premio de risco = 14,8%
KD_LIQ = 0.10 * (1 - ALIQUOTA)   # 6,6%
TICKET = 1200
CHURN = 0.15
PCT_AQUISICAO = 0.02

# ---------------- leitura e limpeza ----------------
arquivo = sys.argv[1] if len(sys.argv) > 1 else "Demonstrativo Fecap v3.csv"
d = pd.read_csv(arquivo, sep=";", encoding="latin1", header=None, names=["ano", "cenario", "conta", "valor"], dtype=str)
d = d.dropna(subset=["conta"])
d["conta"] = d["conta"].str.replace(r"\s+", " ", regex=True).str.strip()
d["valor"] = d["valor"].str.replace(".", "", regex=False).str.replace(",", ".", regex=False).astype(float)
d["ano"] = d["ano"].str.replace("Ano ", "").astype(int)
d["cenario"] = d["cenario"].str.replace("Total Cen_", "").astype(int)

# uma linha por cenário/ano, uma coluna por conta (conta que não existe no ano = 0)
b = d.pivot_table(index=["cenario", "ano"], columns="conta", values="valor")
pl_existe = b["BAL - Patrimônio Líquido"].notna()          # no Ano 12 não existe PL
b = b.fillna(0)
cen = b.index.get_level_values("cenario")

def ant(serie):   # valor do ano anterior (no Ano 1 usa o próprio Ano 1)
    x = serie.groupby(level="cenario").shift(1)
    return x.fillna(serie)

def div(a, c):    # divisão que devolve vazio quando o denominador é zero
    return a / c.replace(0, np.nan)

# ---------------- ajustes do balanço ----------------
divida = -(b["BAL - Empréstimos"] + b["BAL - Emprést"])            # soma das duas linhas de empréstimo
divida_seguinte = divida.groupby(level="cenario").shift(-1).fillna(0)
parcela_cp = (divida - divida_seguinte).clip(lower=0)              # dívida que vence no ano seguinte
pc_aj = -b["BAL - Passivo Circulante"] + b["BAL - Empréstimos"] + parcela_cp
elp_aj = divida - parcela_cp - b["BAL - Prov para Contingências"] - b["BAL - Outros deb"]
exigivel = pc_aj + elp_aj
pl = -b["BAL - Patrimônio Líquido"]
ac, disp, estoq = b["BAL - Ativo Circulante"], b["BAL - Disponível"], b["BAL - Estoques Diversos"]
rlp, perm, at = b["BAL - Realizável a Longo Prazo"], b["BAL - Permanente"], b["BAL - Total do Ativo"]
ok = pl_existe                      # índices de balanço só quando existe PL
ok_pl = pl_existe & (pl > 0)

# ---------------- KPIs ----------------
k = pd.DataFrame(index=b.index)
k["A01"] = b["DRE - Receita"]
k["A03"] = b["DRE - Receita"] + b["DRE - Tributos"]                 # tributos vêm negativos
k["A04"] = -b["DRE - Custos"]
k["A05"] = k["A04"] * PCT_CUSTO_VARIAVEL
k["A07"] = k["A03"] - k["A05"]
k["A08"] = div(k["A07"], k["A03"])
ebit = b["DRE - Resultado Operacional"] + b["DRE - Outros Resultados Operacionais"]
k["A10"] = ebit - b["DRE - Depreciação e Amortização"]
k["A11"] = div(k["A10"], k["A03"])
k["A13"] = b["DRE - Resultado Líquido"]
k["A14"] = div(k["A13"], k["A03"])

k["B01"] = div(ac, pc_aj).where(ok)
k["B02"] = div(ac - estoq, pc_aj).where(ok)
k["B03"] = div(disp, pc_aj).where(ok)
k["B04"] = div(ac + rlp, exigivel).where(ok)
k["B05"] = (ac - pc_aj).where(ok)

k["C01"] = divida
k["C03"] = div(exigivel, at).where(ok)
k["C04"] = div(exigivel, pl).where(ok_pl)
k["C05"] = div(pc_aj, exigivel).where(ok)
k["C06"] = div(perm, pl).where(ok_pl)
k["C07"] = div(perm, pl + elp_aj).where(ok)
k["C08"] = div(divida - disp, k["A10"])
k["C09"] = div(ebit, -b["DRE - Despesas Financeiras"])

capital = ant(pl) + ant(divida)                                    # PL + dívida do início do ano
k["D01"] = ebit * (1 - ALIQUOTA)
k["D06"] = div(ant(pl), capital) * KE + div(ant(divida), capital) * KD_LIQ
k["D08"] = k["D01"] - k["D06"] * capital
mva = []
for (c, a), wacc in k["D06"].items():                              # valor presente dos EVAs futuros
    futuros = k.loc[c, "D08"].loc[a + 1:].values
    mva.append(sum(e / (1 + wacc) ** (i + 1) for i, e in enumerate(futuros)))
k["D09"] = mva

clientes = k["A03"] / TICKET
novos = clientes - ant(clientes) + CHURN * ant(clientes)
novos[novos.index.get_level_values("ano") == 1] = CHURN * clientes    # Ano 1: só reposição do churn
k["E04"] = div(k["A03"] * PCT_AQUISICAO, novos).where(novos > 0)
k["E06"] = div(k["A07"], clientes) / CHURN
k["E07"] = div(k["E06"], k["E04"])

# MVA na data inicial: valor presente dos EVAs dos Anos 1 a 12 pelo WACC do Ano 1
mva0 = {c: sum(e / (1 + g["D06"].iloc[0]) ** (i + 1) for i, e in enumerate(g["D08"].values)) for c, g in k.groupby(level="cenario")}

k.to_csv("kpis_todos_cenarios.csv", sep=";", decimal=",")
base = k.loc[1].copy()
base.loc[0] = np.nan
base.loc[0, "D09"] = mva0[1]                                       # linha "ano 0" = MVA na data inicial
base.sort_index().to_csv("kpis_cenario_base.csv", sep=";", decimal=",")
print("KPIs calculados:", k.shape[1], "indicadores x", len(k), "linhas (cenário x ano)")
print("MVA na data inicial, cenário 1: R$ {:,.0f}".format(mva0[1]))
