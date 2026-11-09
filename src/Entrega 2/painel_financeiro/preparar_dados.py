# preparar_dados.py
# Contabilidade e Finanças - Entrega 02 - Projeto Interdisciplinar CTI (FECAP)
# Professor: Mauricio Lopes da Cunha
# Integrantes: Bruno Nobrega, Kaio Inglez, Mauricio Suster e Yuri Santana
#
# Gera o arquivo que o painel lê (dados/dados_painel.csv) a partir da saída do
# calculo_entrega2.py (indicadores_e2_todos_cenarios.csv, valores em R$ milhões):
# KPIs, fluxo de caixa (10), índices da DFC (8), capital de giro (9) e DVA (11).
# Uso: python preparar_dados.py indicadores_e2_todos_cenarios.csv

import sys
import pandas as pd

arquivo = sys.argv[1] if len(sys.argv) > 1 else "indicadores_e2_todos_cenarios.csv"
e2 = pd.read_csv(arquivo, sep=";", decimal=",")

colunas = [
    "cenario", "ano",
    # KPIs da Entrega 1 que aparecem na aba KPIs
    "receita_bruta", "receita_liquida", "ebitda", "margem_ebitda", "lucro_liquido", "margem_liquida",
    "liquidez_corrente", "endividamento_geral", "divida_liquida_ebitda",
    # 10 - fluxo de caixa (método direto e indireto)
    "recebimentos_clientes", "tributos_pagos", "custos_pagos", "ir_cs_pagos", "receitas_financeiras_recebidas", "fco",
    "fci", "juros_amortizacao_pagos", "dividendos_pagos", "fcf", "variacao_caixa", "saldo_inicial", "saldo_final",
    "depreciacao", "juros_dre", "var_clientes_creditos", "var_impostos_diferidos", "var_swap",
    "var_fornecedores_obrigacoes", "var_provisao_manutencao", "outros_ajustes",
    # 8 - índices da DFC
    "cobertura_juros_caixa", "cobertura_servico_divida", "qualidade_resultado", "margem_caixa", "retorno_caixa_ativo",
    "retorno_caixa_pl", "cobertura_dividendos", "capacidade_investimento", "fluxo_caixa_livre", "anos_pagar_divida",
    # 9 - capital de giro
    "ac", "acf", "acc", "pcf", "pcc", "ncg", "saldo_tesouraria", "ccl", "cdg", "pmr", "pmp", "pme",
    "ciclo_operacional", "ciclo_financeiro", "tipo_fleuriet",
    # 11 - DVA
    "outras_receitas", "insumos", "va_bruto", "va_liquido", "va_transferencia", "va_total", "dist_impostos",
    "dist_terceiros", "dist_acionistas", "pct_governo", "pct_terceiros", "pct_acionistas", "va_sobre_receita",
    # conferências (têm que dar zero)
    "conf_saldo_final", "conf_geracao", "conf_dva", "conf_capital_giro",
]

dados = e2[colunas]
dados.round(6).to_csv("dados/dados_painel.csv", sep=";", decimal=",", index=False)
print("dados/dados_painel.csv:", dados.shape[0], "linhas e", dados.shape[1], "colunas")
