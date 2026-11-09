# calculo_entrega2.py
# Contabilidade e Finanças - Entrega 02 - Projeto Interdisciplinar CTI (FECAP)
# Professor: Mauricio Lopes da Cunha
# Integrantes: Bruno Nobrega, Kaio Inglez, Mauricio Suster e Yuri Santana
#
# Calcula, para todos os cenários e anos:
#   10 - Fluxo de caixa (DFC método direto, por atividade)
#    8 - Índices da DFC
#    9 - Índices de capital de giro (NCG, saldo de tesouraria, CDG, modelo Fleuriet, prazos e ciclos)
#   11 - DVA (Demonstração do Valor Adicionado)
# Uso: python calculo_entrega2.py "Demonstrativo Fecap v3.csv"
# Saídas: indicadores_e2_todos_cenarios.csv e indicadores_e2_cenario_1.csv (valores em R$ milhões)

import sys
import numpy as np
import pandas as pd

DIAS = 360   # ano comercial para os prazos médios


def carregar(caminho):
    d = pd.read_csv(caminho, sep=";", encoding="latin1", header=None, names=["ano", "cenario", "conta", "valor"], dtype=str)
    d = d.dropna(subset=["conta"])
    d["conta"] = d["conta"].str.replace(r"\s+", " ", regex=True).str.strip()
    d["valor"] = d["valor"].str.replace(".", "", regex=False).str.replace(",", ".", regex=False).astype(float) / 1e6
    d["ano"] = d["ano"].str.replace("Ano ", "").astype(int)
    d["cenario"] = d["cenario"].str.replace("Total Cen_", "").astype(int)
    w = d.pivot_table(index=["cenario", "ano"], columns="conta", values="valor")
    return w


def calcular(w):
    tem_pl = w["BAL - Patrimônio Líquido"].notna()        # no Ano 12 não há balanço completo
    b = w.fillna(0)
    g = lambda conta: b[conta]
    ant = lambda s: s.groupby(level="cenario").shift(1)   # valor do ano anterior
    r = pd.DataFrame(index=w.index)

    # ---------- 10. Fluxo de caixa (método direto) ----------
    r["recebimentos_clientes"] = g("FLU - Receita")
    r["tributos_pagos"] = g("FLU - Tributos")
    r["custos_pagos"] = g("FLU - Custos")
    r["ir_cs_pagos"] = g("FLU - Imposto de Renda e Contribuição Social")
    r["receitas_financeiras_recebidas"] = g("FLU - Entradas")
    r["fco"] = r[["recebimentos_clientes", "tributos_pagos", "custos_pagos", "ir_cs_pagos", "receitas_financeiras_recebidas"]].sum(axis=1)
    r["fci"] = g("FLU - Investimentos")
    r["juros_amortizacao_pagos"] = g("FLU - Despesas Financeiras")
    r["dividendos_pagos"] = g("FLU - Distribuição para Acionista")
    r["fcf"] = r["juros_amortizacao_pagos"] + r["dividendos_pagos"]
    r["variacao_caixa"] = r["fco"] + r["fci"] + r["fcf"]
    r["saldo_inicial"] = g("FLU - Saldo Inicial")
    r["saldo_final"] = r["saldo_inicial"] + r["variacao_caixa"]

    # método indireto (Anos 2 a 11: precisa do balanço do ano anterior)
    r["lucro_liquido"] = g("DRE - Resultado Líquido")
    r["depreciacao"] = -g("DRE - Depreciação e Amortização")
    r["juros_dre"] = -g("DRE - Despesas Financeiras")
    grupos = {
        "var_clientes_creditos": ["BAL - Contas a Receber - Clientes", "BAL - Contas a Receber - Partes Relacionadas",
                                  "BAL - Outros Créditos", "BAL - Estoques Diversos"],
        "var_impostos_diferidos": ["BAL - At Fiscal Diferido", "BAL - Créditos Tributários", "BAL - Outros Créditos LP"],
        "var_swap": ["BAL - Contas a Receber - SWAP"],
        "var_fornecedores_obrigacoes": ["BAL - Fornecedores", "BAL - Encargos Sociais e Trabalhistas", "BAL - Tributos a pagar",
                                        "BAL - Impostos", "BAL - Obrigações com o Poder Concedente", "BAL - Outros Débitos",
                                        "BAL - Contas a Pagar - Parte Relacionada"],
        "var_provisao_manutencao": ["BAL - Provisão Manutenção"],
    }
    ano = w.index.get_level_values("ano")
    valido_ind = (ano >= 2) & (ano <= 11)
    for nome, contas in grupos.items():
        s = b[contas].sum(axis=1)
        r[nome] = (-(s - ant(s))).where(valido_ind)          # aumento de ativo tira caixa; aumento de obrigação põe caixa
    soma = r[["lucro_liquido", "depreciacao", "juros_dre"] + list(grupos)].sum(axis=1)
    r["outros_ajustes"] = (r["fco"] - soma).where(valido_ind)

    # ---------- 9. Capital de giro ----------
    divida = -(g("BAL - Empréstimos") + g("BAL - Emprést"))
    seguinte = divida.groupby(level="cenario").shift(-1).fillna(0)
    r["ac"] = g("BAL - Ativo Circulante")
    r["acf"] = g("BAL - Disponível") + g("BAL - Contas a Receber - SWAP")             # ativo circulante financeiro
    r["acc"] = r["ac"] - r["acf"]                                                       # ativo circulante cíclico
    r["pcf"] = (divida - seguinte).clip(lower=0)                                        # parte da dívida que vence no ano seguinte
    r["pcc"] = -g("BAL - Passivo Circulante") + g("BAL - Empréstimos")                  # passivo circulante cíclico
    pl = -g("BAL - Patrimônio Líquido")
    elp = divida - r["pcf"] - g("BAL - Prov para Contingências") - g("BAL - Outros deb")
    r["ncg"] = r["acc"] - r["pcc"]
    r["saldo_tesouraria"] = r["acf"] - r["pcf"]
    r["ccl"] = r["ac"] - (r["pcc"] + r["pcf"])
    r["cdg"] = pl + elp - g("BAL - Realizável a Longo Prazo") - g("BAL - Permanente")
    r["pmr"] = g("BAL - Contas a Receber - Clientes") / g("DRE - Receita") * DIAS
    r["pmp"] = -g("BAL - Fornecedores") / -g("DRE - Custos") * DIAS
    r["pme"] = g("BAL - Estoques Diversos") / -g("DRE - Custos") * DIAS
    r["ciclo_operacional"] = r["pme"] + r["pmr"]
    r["ciclo_financeiro"] = r["ciclo_operacional"] - r["pmp"]
    r["liquidez_corrente"] = r["ac"] / (r["pcc"] + r["pcf"])
    r["endividamento_geral"] = (r["pcc"] + r["pcf"] + elp) / g("BAL - Total do Ativo")
    for col in ["ac", "acf", "acc", "pcf", "pcc", "ncg", "saldo_tesouraria", "ccl", "cdg", "pmr", "pmp", "pme",
                "ciclo_operacional", "ciclo_financeiro", "liquidez_corrente", "endividamento_geral"]:
        r[col] = r[col].where(tem_pl)

    def tipo(cdg, ncg, st):
        if pd.isna(cdg): return "n/a"
        if cdg > 0 and ncg < 0 and st > 0: return "Tipo 1 - Excelente"
        if cdg > 0 and ncg > 0 and st > 0: return "Tipo 2 - Sólida"
        if cdg > 0 and ncg > 0 and st < 0: return "Tipo 3 - Insatisfatória"
        if cdg < 0 and ncg > 0 and st < 0: return "Tipo 4 - Péssima"
        if cdg < 0 and ncg < 0 and st < 0: return "Tipo 5 - Muito ruim"
        if cdg < 0 and ncg < 0 and st > 0: return "Tipo 6 - Alto risco"
        return "Indefinido"
    r["tipo_fleuriet"] = [tipo(a, n, s) for a, n, s in zip(r["cdg"], r["ncg"], r["saldo_tesouraria"])]

    # ---------- 11. DVA ----------
    r["receita_bruta"] = g("DRE - Receita")
    r["outras_receitas"] = g("DRE - Outros Resultados Operacionais")
    r["insumos"] = -g("DRE - Custos")
    r["va_bruto"] = r["receita_bruta"] + r["outras_receitas"] - r["insumos"]
    r["va_liquido"] = r["va_bruto"] - r["depreciacao"]
    r["va_transferencia"] = g("DRE - Receitas Financeiras")
    r["va_total"] = r["va_liquido"] + r["va_transferencia"]
    r["dist_impostos"] = -g("DRE - Tributos") - g("DRE - Imposto de Renda e Contribuição Social")
    r["dist_terceiros"] = r["juros_dre"]
    r["dist_acionistas"] = r["lucro_liquido"]
    r["pct_governo"] = r["dist_impostos"] / r["va_total"]
    r["pct_terceiros"] = r["dist_terceiros"] / r["va_total"]
    r["pct_acionistas"] = r["dist_acionistas"] / r["va_total"]
    r["va_sobre_receita"] = r["va_total"] / r["receita_bruta"]

    # ---------- 8. Índices da DFC ----------
    receita_liquida = g("DRE - Receita") + g("DRE - Tributos")
    r["receita_liquida"] = receita_liquida
    r["cobertura_juros_caixa"] = r["fco"] / r["juros_dre"]
    r["cobertura_servico_divida"] = r["fco"] / -r["juros_amortizacao_pagos"]
    r["qualidade_resultado"] = r["fco"] / r["lucro_liquido"]
    r["margem_caixa"] = r["fco"] / receita_liquida
    r["retorno_caixa_ativo"] = (r["fco"] / g("BAL - Total do Ativo")).where(tem_pl)
    r["retorno_caixa_pl"] = (r["fco"] / pl).where(tem_pl & (pl > 0))
    r["cobertura_dividendos"] = r["fco"] / -r["dividendos_pagos"]
    r["capacidade_investimento"] = r["fco"] / -r["fci"]
    r["fluxo_caixa_livre"] = r["fco"] + r["fci"]
    r["anos_pagar_divida"] = divida / r["fco"]

    # ---------- KPIs da Entrega 1 usados aqui ----------
    r["ebitda"] = receita_liquida - (-g("DRE - Custos")) + g("DRE - Outros Resultados Operacionais")
    r["margem_ebitda"] = r["ebitda"] / receita_liquida
    r["margem_liquida"] = r["lucro_liquido"] / receita_liquida
    r["divida_liquida_ebitda"] = (divida - g("BAL - Disponível")) / r["ebitda"]

    # conferências
    r["conf_saldo_final"] = r["saldo_final"] - g("BAL - Disponível")
    r["conf_geracao"] = r["variacao_caixa"] - g("FLU - Geração de Caixa")
    r["conf_dva"] = r["va_total"] - (r["dist_impostos"] + r["dist_terceiros"] + r["dist_acionistas"])
    r["conf_capital_giro"] = r["ccl"] - (r["ncg"] + r["saldo_tesouraria"])
    return r


if __name__ == "__main__":
    caminho = sys.argv[1] if len(sys.argv) > 1 else "Demonstrativo Fecap v3.csv"
    r = calcular(carregar(caminho))
    r.to_csv("indicadores_e2_todos_cenarios.csv", sep=";", decimal=",")
    r.loc[1].to_csv("indicadores_e2_cenario_1.csv", sep=";", decimal=",")
    print("Linhas calculadas:", len(r))
    for c in ["conf_saldo_final", "conf_geracao", "conf_dva", "conf_capital_giro"]:
        print(f"{c}: maior diferença = R$ {r[c].abs().max():.6f} milhões")
