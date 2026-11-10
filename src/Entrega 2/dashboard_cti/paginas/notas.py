# paginas/notas.py - fontes, fórmulas, premissas, contribuição de cada disciplina e limitações

import pandas as pd
import streamlit as st

from dados import KPIS, COMPLEMENTARES
from formatos import cabecalho

ctx = st.session_state["ctx"]
cabecalho("Notas metodológicas", ctx)

st.markdown(f"""
**Fonte:** arquivo *Demonstrativo Fecap v3.csv* enviado pela CTI Global (balanço, DRE e fluxo de caixa de uma
concessionária, 12 anos × 1.200 cenários simulados). O dashboard lê a *base_cti_processada.csv*, gerada na Entrega 1
pelo notebook *Preparacao_Dados_CTI.ipynb*. Última atualização do arquivo: {ctx['atualizado']}.

**Unidades:** R\\$ milhões nominais (sem correção pela inflação), margens e percentuais em %, dívida líquida / EBITDA em
vezes. Os números seguem o padrão brasileiro (1.234,5).

**Mediana e faixa:** a mediana e a faixa P10 a P90 são calculadas com os cenários do grupo escolhido no filtro, ano a ano.
""")

st.subheader("Fórmulas dos indicadores")
st.dataframe(pd.DataFrame([{"Código": c, "Indicador": n, "Fórmula": f, "Tipo": "KPI principal" if (c, n) in
                            [(k[0], k[1]) for k in KPIS] else "Complementar"} for c, n, _, _, f in KPIS + COMPLEMENTARES]),
             hide_index=True, width="stretch")
st.caption("Os códigos são os do dicionário de KPIs da Entrega 1 de Contabilidade. \"–\" = indicador de apoio sem código no dicionário.")

st.subheader("Premissas do simulador de sensibilidade")
st.markdown("""
- A DRE do ano é refeita com as variações: EBITDA = receita líquida − custos + outros resultados, e lucro antes do
  IR/CSLL = EBITDA − depreciação + resultado financeiro.
- Os tributos sobre a receita acompanham a receita, então a receita líquida varia no mesmo percentual.
- A alíquota efetiva de IR/CSLL é a do próprio cenário e ano (cerca de 34,4%). Se o resultado antes do imposto ficar
  negativo, não há IR/CSLL.
- Caixa e dívida não mudam, então a dívida líquida / EBITDA muda só pelo EBITDA.
- Pessimista, realista e otimista são os percentis 10, 50 e 90 dos cenários do grupo em cada ano.
""")

st.subheader("O que cada disciplina trouxe para o dashboard")
st.dataframe(pd.DataFrame([
    ("PI Ciência de Dados", "Preparação da base (Entrega 1), dashboard, filtros, comparações e regras de qualidade"),
    ("Contabilidade e Finanças", "Dicionário de KPIs, fórmulas, planilha de validação e análise de sensibilidade"),
    ("Análise Inferencial", "Distribuições e boxplots (Entrega 1) e modelos de regressão (Entrega 2)"),
    ("Engenharia de Software", "Arquitetura em camadas, separação entre dados, cálculo e telas, README e testes"),
], columns=["Disciplina", "Contribuição"]), hide_index=True, width="stretch")

st.subheader("Limitações")
st.markdown("""
- Os dados são cenários simulados pela CTI, não resultados reais da empresa.
- O EBITDA é calculado pela DRE, como no dicionário. O arquivo traz outra linha de EBITDA, em média R\\$ 301 milhões
  maior, que não usamos.
- O Ano 12 é atípico (fim da concessão): a dívida é zerada, os dividendos sobem muito e a margem EBITDA passa de 100%.
  Por isso os cartões começam no Ano 11.
- O patrimônio líquido não existe no Ano 12, então o endividamento geral fica n/a nesse ano.
- Os cenários 1001 a 1200 se comportam de forma diferente dos cenários 1 a 1000, por isso existe o filtro de grupo.
- O simulador muda um ano de cada vez e não recalcula os anos seguintes.
- As comparações e as regressões mostram associação entre variáveis, não causa e efeito.
- Os dados da CTI são confidenciais: a publicação na nuvem depende da autorização da empresa.
""")
