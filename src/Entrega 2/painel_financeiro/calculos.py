# calculos.py
# Contabilidade e Finanças - Entrega 02 - Projeto Interdisciplinar CTI (FECAP)
# Professor: Mauricio Lopes da Cunha
# Integrantes: Bruno Nobrega, Kaio Inglez, Mauricio Suster e Yuri Santana
#
# Listas de indicadores e montagem das tabelas do painel (DFC, método indireto e DVA).
# Os valores vêm prontos do calculo_entrega2.py (os mesmos da Planilha_Entrega02_Contabilidade_CTI.xlsx).
# Valores em R$ milhões. O app.py só chama estas funções.

import pandas as pd


def carregar_dados(caminho):
    """Lê o arquivo gerado pelo preparar_dados.py."""
    return pd.read_csv(caminho, sep=";", decimal=",")


# tipos de formatação: rs = R$ milhões, pct = %, x = vezes, dias, anos, txt = texto
# (código, nome, coluna, tipo, fórmula)
KPIS_E1 = [
    ("A03", "Receita líquida", "receita_liquida", "rs", "Receita bruta − tributos"),
    ("A10", "EBITDA", "ebitda", "rs", "Resultado operacional + outros resultados + depreciação e amortização"),
    ("A11", "Margem EBITDA", "margem_ebitda", "pct", "EBITDA / receita líquida"),
    ("A14", "Margem líquida", "margem_liquida", "pct", "Lucro líquido / receita líquida"),
    ("B01", "Liquidez corrente", "liquidez_corrente", "x", "Ativo circulante / passivo circulante ajustado"),
    ("C03", "Endividamento geral", "endividamento_geral", "pct", "Passivo exigível (circulante + longo prazo) / ativo total"),
    ("C08", "Dívida líquida / EBITDA", "divida_liquida_ebitda", "x", "(Dívida − caixa) / EBITDA"),
]
KPIS_E2 = [
    ("H01", "Fluxo de caixa operacional (FCO)", "fco", "rs", "Recebimentos − pagamentos da operação (aba 10)"),
    ("H02", "Fluxo de caixa livre", "fluxo_caixa_livre", "rs", "FCO + FCI (aba 8)"),
    ("H03", "Qualidade do resultado", "qualidade_resultado", "x", "FCO / lucro líquido (aba 8)"),
    ("H04", "Cobertura do serviço da dívida", "cobertura_servico_divida", "x", "FCO / (juros + amortização pagos) (aba 8)"),
    ("H05", "Necessidade de capital de giro (NCG)", "ncg", "rs", "ACC − PCC (aba 9)"),
    ("H06", "Saldo de tesouraria", "saldo_tesouraria", "rs", "ACF − PCF (aba 9)"),
    ("H07", "Ciclo financeiro", "ciclo_financeiro", "dias", "PME + PMR − PMP (aba 9)"),
    ("H08", "Estrutura financeira (Fleuriet)", "tipo_fleuriet", "txt", "Sinais de CDG, NCG e saldo de tesouraria (aba 9)"),
    ("H09", "Valor adicionado total", "va_total", "rs", "Valor adicionado líquido + recebido em transferência (aba 11)"),
    ("H10", "Valor adicionado para os acionistas", "pct_acionistas", "pct", "Lucro líquido / valor adicionado total (aba 11)"),
    ("H11", "Valor adicionado para o governo", "pct_governo", "pct", "(Tributos + IR/CSLL) / valor adicionado total (aba 11)"),
]

# (nome, coluna, tipo, fórmula, como ler)
INDICES_DFC = [
    ("Cobertura de juros com caixa", "cobertura_juros_caixa", "x", "FCO / juros da DRE", "Quantas vezes o caixa da operação paga os juros"),
    ("Cobertura do serviço da dívida", "cobertura_servico_divida", "x", "FCO / (juros + amortização pagos)", "Acima de 1x a operação paga a dívida do ano"),
    ("Qualidade do resultado", "qualidade_resultado", "x", "FCO / lucro líquido", "Acima de 1 o lucro vira caixa"),
    ("Margem de caixa", "margem_caixa", "pct", "FCO / receita líquida", "Quanto de cada R$ 1 de receita vira caixa"),
    ("Retorno de caixa sobre o ativo", "retorno_caixa_ativo", "pct", "FCO / ativo total", "Caixa gerado pelos ativos"),
    ("Retorno de caixa sobre o PL", "retorno_caixa_pl", "pct", "FCO / patrimônio líquido", "n/a quando o PL é negativo"),
    ("Cobertura de dividendos", "cobertura_dividendos", "x", "FCO / dividendos pagos", "Abaixo de 1x paga dividendo com caixa guardado"),
    ("Capacidade de investimento", "capacidade_investimento", "x", "FCO / investimentos", "Quantas vezes o FCO paga os investimentos"),
    ("Fluxo de caixa livre", "fluxo_caixa_livre", "rs", "FCO + FCI", "Caixa que sobra depois dos investimentos"),
    ("Anos para pagar a dívida", "anos_pagar_divida", "anos", "Dívida bruta / FCO", "Quanto menor, melhor"),
]

CAPITAL_GIRO = [
    ("Ativo circulante financeiro (ACF)", "acf", "rs", "Disponível + SWAP"),
    ("Ativo circulante cíclico (ACC)", "acc", "rs", "Ativo circulante − ACF"),
    ("Passivo circulante financeiro (PCF)", "pcf", "rs", "Parte da dívida que vence no ano seguinte"),
    ("Passivo circulante cíclico (PCC)", "pcc", "rs", "Passivo circulante − empréstimos"),
    ("Necessidade de capital de giro (NCG)", "ncg", "rs", "ACC − PCC"),
    ("Saldo de tesouraria (ST)", "saldo_tesouraria", "rs", "ACF − PCF"),
    ("Capital de giro (CDG)", "cdg", "rs", "PL + exigível LP − realizável LP − permanente"),
    ("Capital circulante líquido (CCL)", "ccl", "rs", "Ativo circulante − passivo circulante (= NCG + ST)"),
    ("Prazo médio de recebimento (PMR)", "pmr", "dias", "Clientes / receita bruta × 360"),
    ("Prazo médio de pagamento (PMP)", "pmp", "dias", "Fornecedores / custos × 360"),
    ("Prazo médio de estocagem (PME)", "pme", "dias", "Estoques / custos × 360"),
    ("Ciclo operacional", "ciclo_operacional", "dias", "PME + PMR"),
    ("Ciclo financeiro", "ciclo_financeiro", "dias", "Ciclo operacional − PMP"),
]

# modelo Fleuriet: sinais de CDG, NCG e ST
FLEURIET = pd.DataFrame([
    ("Tipo 1 - Excelente", "+", "−", "+", "Sobra caixa e a operação ainda financia a empresa"),
    ("Tipo 2 - Sólida", "+", "+", "+", "Recursos de longo prazo cobrem a NCG e sobra caixa"),
    ("Tipo 3 - Insatisfatória", "+", "+", "−", "Depende de dívida de curto prazo para o giro"),
    ("Tipo 4 - Péssima", "−", "+", "−", "Giro e longo prazo financiados com dívida curta"),
    ("Tipo 5 - Muito ruim", "−", "−", "−", "A operação gera recursos, mas falta caixa"),
    ("Tipo 6 - Alto risco", "−", "−", "+", "Caixa vem da operação, longo prazo descoberto"),
], columns=["Tipo", "CDG", "NCG", "ST", "Leitura"])


def linhas_dfc(l):
    """DFC pelo método direto (aba 10). Devolve (linha, valor, é total?)."""
    return [
        ("Recebimentos de clientes", l["recebimentos_clientes"], False),
        ("Tributos pagos", l["tributos_pagos"], False),
        ("Custos pagos", l["custos_pagos"], False),
        ("IR e CSLL pagos", l["ir_cs_pagos"], False),
        ("Receitas financeiras recebidas", l["receitas_financeiras_recebidas"], False),
        ("Fluxo de caixa operacional (FCO)", l["fco"], True),
        ("Investimentos", l["fci"], False),
        ("Fluxo de caixa de investimento (FCI)", l["fci"], True),
        ("Juros e amortização pagos", l["juros_amortizacao_pagos"], False),
        ("Dividendos pagos", l["dividendos_pagos"], False),
        ("Fluxo de caixa de financiamento (FCF)", l["fcf"], True),
        ("Variação do caixa (FCO + FCI + FCF)", l["variacao_caixa"], True),
        ("Saldo inicial de caixa", l["saldo_inicial"], False),
        ("Saldo final de caixa", l["saldo_final"], True),
    ]


def linhas_indireto(l):
    """FCO pelo método indireto (Anos 2 a 11, precisa do balanço do ano anterior)."""
    return [
        ("Lucro líquido", l["lucro_liquido"], False),
        ("(+) Depreciação e amortização", l["depreciacao"], False),
        ("(+) Juros da DRE (estão no financiamento)", l["juros_dre"], False),
        ("Variação de clientes, créditos e estoques", l["var_clientes_creditos"], False),
        ("Variação de impostos diferidos e créditos LP", l["var_impostos_diferidos"], False),
        ("Variação do SWAP a receber", l["var_swap"], False),
        ("Variação de fornecedores e obrigações", l["var_fornecedores_obrigacoes"], False),
        ("Variação da provisão de manutenção", l["var_provisao_manutencao"], False),
        ("Outros ajustes não identificados", l["outros_ajustes"], False),
        ("Fluxo de caixa operacional (FCO)", l["fco"], True),
    ]


def linhas_dva(l):
    """DVA (aba 11): geração e distribuição do valor adicionado."""
    geracao = [
        ("Receita bruta", l["receita_bruta"], False),
        ("Outras receitas operacionais", l["outras_receitas"], False),
        ("(−) Insumos adquiridos de terceiros (custos)", -l["insumos"], False),
        ("Valor adicionado bruto", l["va_bruto"], True),
        ("(−) Depreciação e amortização", -l["depreciacao"], False),
        ("Valor adicionado líquido", l["va_liquido"], True),
        ("(+) Recebido em transferência (receitas financeiras)", l["va_transferencia"], False),
        ("Valor adicionado total a distribuir", l["va_total"], True),
    ]
    distribuicao = [
        ("Governo (tributos + IR/CSLL)", l["dist_impostos"], l["pct_governo"]),
        ("Terceiros (juros)", l["dist_terceiros"], l["pct_terceiros"]),
        ("Acionistas (lucro líquido)", l["dist_acionistas"], l["pct_acionistas"]),
        ("Total distribuído", l["dist_impostos"] + l["dist_terceiros"] + l["dist_acionistas"], 1.0),
    ]
    return geracao, distribuicao
