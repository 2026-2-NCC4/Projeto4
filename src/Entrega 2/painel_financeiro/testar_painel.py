# testar_painel.py
# Contabilidade e Finanças - Entrega 02 - Projeto Interdisciplinar CTI (FECAP)
# Integrantes: Bruno Nobrega, Kaio Inglez, Mauricio Suster e Yuri Santana
#
# Confere se o painel mostra os mesmos números da planilha da Entrega 2 (cenário 1).
# Uso: python testar_painel.py "caminho/Planilha_Entrega02_Contabilidade_CTI.xlsx"

import sys
import pandas as pd
from openpyxl import load_workbook
from calculos import carregar_dados

planilha = sys.argv[1] if len(sys.argv) > 1 else "Planilha_Entrega02_Contabilidade_CTI.xlsx"
wb = load_workbook(planilha, data_only=True)

# aba da planilha: {texto da linha (coluna A): coluna do painel}
PARES = {
    "KPIs": {"A03": "receita_liquida", "A10": "ebitda", "A11": "margem_ebitda", "A14": "margem_liquida",
             "B01": "liquidez_corrente", "C03": "endividamento_geral", "C08": "divida_liquida_ebitda",
             "H01": "fco", "H02": "fluxo_caixa_livre", "H03": "qualidade_resultado", "H04": "cobertura_servico_divida",
             "H05": "ncg", "H06": "saldo_tesouraria", "H07": "ciclo_financeiro", "H08": "tipo_fleuriet",
             "H09": "va_total", "H10": "pct_acionistas", "H11": "pct_governo"},
    "8_Indices_DFC": {"Cobertura de juros com caixa": "cobertura_juros_caixa",
                      "Cobertura do serviço da dívida": "cobertura_servico_divida",
                      "Qualidade do resultado": "qualidade_resultado", "Margem de caixa": "margem_caixa",
                      "Retorno de caixa sobre o ativo": "retorno_caixa_ativo", "Retorno de caixa sobre o PL": "retorno_caixa_pl",
                      "Cobertura de dividendos": "cobertura_dividendos", "Capacidade de investimento": "capacidade_investimento",
                      "Fluxo de caixa livre": "fluxo_caixa_livre", "Anos para pagar a dívida": "anos_pagar_divida"},
    "9_Capital_de_Giro": {"Ativo circulante financeiro": "acf", "Ativo circulante cíclico": "acc",
                          "Passivo circulante financeiro": "pcf", "Passivo circulante cíclico": "pcc",
                          "(=) Necessidade de capital de giro": "ncg", "(=) Saldo de tesouraria": "saldo_tesouraria",
                          "(=) Capital de giro": "cdg", "Capital circulante líquido": "ccl",
                          "Estrutura financeira": "tipo_fleuriet", "Prazo médio de recebimento": "pmr",
                          "Prazo médio de pagamento": "pmp", "Prazo médio de estocagem": "pme",
                          "(=) Ciclo operacional": "ciclo_operacional", "(=) Ciclo financeiro": "ciclo_financeiro"},
    "10_Fluxo_de_Caixa": {"Recebimentos de clientes": "recebimentos_clientes", "Tributos sobre a receita pagos": "tributos_pagos",
                          "Pagamentos de custos": "custos_pagos", "IR e CSLL pagos": "ir_cs_pagos",
                          "Receitas financeiras recebidas": "receitas_financeiras_recebidas",
                          "(=) Fluxo de caixa operacional": "fco", "(=) Fluxo de caixa de investimento": "fci",
                          "Juros e amortização": "juros_amortizacao_pagos", "Dividendos pagos": "dividendos_pagos",
                          "(=) Fluxo de caixa de financiamento": "fcf", "(=) Variação do caixa": "variacao_caixa",
                          "Saldo inicial de caixa": "saldo_inicial", "(=) Saldo final de caixa": "saldo_final",
                          "(±) Variação de clientes": "var_clientes_creditos", "(±) Variação de impostos": "var_impostos_diferidos",
                          "(±) Variação do SWAP": "var_swap", "(±) Variação de fornecedores": "var_fornecedores_obrigacoes",
                          "(±) Variação da provisão": "var_provisao_manutencao", "(±) Outros ajustes": "outros_ajustes"},
    "11_DVA": {"(=) 3. Valor adicionado bruto": "va_bruto", "(=) 5. Valor adicionado líquido": "va_liquido",
               "6. Valor adicionado recebido": "va_transferencia", "(=) 7. Valor adicionado total": "va_total",
               "8.2 Impostos": "dist_impostos", "8.3 Remuneração de capitais de terceiros": "dist_terceiros",
               "8.4 Remuneração de capitais próprios": "dist_acionistas", "Parte do valor adicionado para o governo": "pct_governo",
               "Parte para os financiadores": "pct_terceiros", "Parte para os acionistas": "pct_acionistas",
               "Valor adicionado sobre a receita": "va_sobre_receita"},
}


def igual(x, y):
    vazio = lambda v: v is None or v == "n/a" or (isinstance(v, float) and pd.isna(v))
    if vazio(x) or vazio(y):
        return vazio(x) and vazio(y)
    if isinstance(x, str) or isinstance(y, str):
        return str(x) == str(y)
    return abs(x - y) <= 1e-6 * max(1, abs(y))     # o arquivo do painel guarda 6 casas decimais


dados = carregar_dados("dados/dados_painel.csv")
c1 = dados[dados["cenario"] == 1].set_index("ano")

total, erros = 0, []
for aba, pares in PARES.items():
    ws = wb[aba]
    linhas = {str(r[0].value).strip(): r[0].row for r in ws.iter_rows(min_col=1, max_col=1) if r[0].value}
    for inicio, coluna in pares.items():
        # linha que começa com o texto e tem valores (pula títulos e observações)
        achou = [n for n in linhas if n.startswith(inicio) and ws.cell(row=linhas[n], column=2).value is not None]
        if not achou:
            erros.append((aba, inicio, "linha não encontrada na planilha"))
            continue
        linha = linhas[achou[0]]
        for ano in range(1, 13):
            total += 1
            esperado = ws.cell(row=linha, column=1 + ano).value
            obtido = c1.loc[ano, coluna]
            if not igual(obtido, esperado):
                erros.append((aba, inicio, ano, esperado, obtido))
    print(f"{aba}: {len(pares)} indicadores conferidos")

print(f"Painel x planilha da Entrega 2: {total} comparações, {total - len(erros)} iguais, {len(erros)} diferentes")
for e in erros[:10]:
    print("  diferente:", e)

# conferências contábeis em todos os 1.200 cenários (têm que ser zero)
for col, nome in [("conf_saldo_final", "saldo final x caixa do balanço"), ("conf_geracao", "variação x geração de caixa"),
                  ("conf_dva", "valor adicionado x distribuído"), ("conf_capital_giro", "CCL x NCG + ST")]:
    print(f"Conferência {nome}: maior diferença = R$ {dados[col].abs().max():.6f} milhões")
