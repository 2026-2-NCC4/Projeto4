# Entregas do PI
### **DECLARAÇÃO DE USO DE INTELIGÊNCIA ARTIFICIAL**

Declaração feita no modelo padronizado do Art. 7º do Guia para o Uso Responsável de Inteligência Artificial na FECAP (versão 2.0, de 29 de julho de 2026).

## Identificação

| **Alunos** | **RA** |
| :--- | :--- |
| Bruno Nobrega | 25027405 |
| Kaio Inglez | 24026741 |
| Mauricio Suster | 24026985 |
| Yuri Santana | 25027408 |

| **Curso / Turma** | Ciência da Computação – 4º semestre |
| :--- | :--- |
| **Projeto** | Projeto Interdisciplinar – Plataforma Analítica de Planejamento Financeiro (CTI Global) |
| **Professores** | Eduardo Savino Gomes – PI Ciência de Dados<br>Mauricio Lopes da Cunha – Contabilidade e Finanças<br>Rodinil da Silva Moreira Lisboa – Análise Inferencial de Dados<br>Luiz – Engenharia de Software e Arquitetura de Sistemas |
| **Ferramenta utilizada** | Claude (Anthropic) |
| **Versão/modelo** | Claude Opus 5.5 |

Os *prompts* abaixo estão resumidos e com a redação ajustada. O histórico completo da conversa com a ferramenta pode ser apresentado se solicitado.

## Entrega 1
<br><br>

Os códigos da Entrega 1 ficam junto com as entregas, na pasta `Documentos/Entrega 1`.

### Módulo de preparação dos dados

| **Aluno(s) Responsável(veis)** | Mauricio Suster (uso da ferramenta), com Bruno Nobrega, Kaio Inglez e Yuri Santana |
| :--- | :--- |
| **Ferramenta utilizada** | Claude (Anthropic) |
| **Versão/modelo** | Claude Opus 5.5 |
| **Disciplina / Trabalho** | PI Ciência de Dados – Entrega 1: notebook de coleta, limpeza e integração dos dados |
| **Finalidade de uso** | Geração do código do notebook que lê o arquivo da CTI, limpa, padroniza, integra e grava a base `base_cti_processada.csv`, e correção dos comentários do notebook. |
| ***Prompts* principais utilizados** | 1. Faça a preparação dos dados da Entrega 1 de PI Ciência de Dados em notebook do Colab, com relatório de 3 a 4 páginas.<br>2. Corrija os comentários dos notebooks que aparecem com problema no Colab. |
| **Trechos ou entregas afetadas** | `Documentos/Entrega 1/Projeto Interdisciplinar Ciencia de Dados/Preparacao_Dados_CTI.ipynb` |


### Módulo de cálculo dos KPIs

| **Aluno(s) Responsável(veis)** | Mauricio Suster (uso da ferramenta), com Bruno Nobrega, Kaio Inglez e Yuri Santana |
| :--- | :--- |
| **Ferramenta utilizada** | Claude (Anthropic) |
| **Versão/modelo** | Claude Opus 5.5 |
| **Disciplina / Trabalho** | Contabilidade e Finanças – Entrega 1: script de cálculo dos KPIs |
| **Finalidade de uso** | Geração do script em Python que calcula os KPIs do dicionário para todos os cenários e anos e gera os arquivos usados na planilha de validação. |
| ***Prompts* principais utilizados** | 1. Elabore a Entrega 1 de Contabilidade e Finanças a partir do enunciado e dos dados da CTI: dicionário de KPIs, planilha de validação e script de cálculo em Python. |
| **Trechos ou entregas afetadas** | `Documentos/Entrega 1/Contabilidade e Finanças/calculo_kpis.py` |

### Módulo de análise descritiva

| **Aluno(s) Responsável(veis)** | Mauricio Suster (uso da ferramenta), com Bruno Nobrega, Kaio Inglez e Yuri Santana |
| :--- | :--- |
| **Ferramenta utilizada** | Claude (Anthropic) |
| **Versão/modelo** | Claude Opus 5.5 |
| **Disciplina / Trabalho** | Análise Inferencial de Dados – Entrega 1: notebook de análise descritiva |
| **Finalidade de uso** | Geração do código do notebook com as medidas de posição e dispersão, os histogramas, os boxplots e a análise de outliers. |
| ***Prompts* principais utilizados** | 1. Faça a análise descritiva dos dados (Entrega 1 de Análise Inferencial) de forma enxuta, em até 4 páginas. |
| **Trechos ou entregas afetadas** | `Documentos/Entrega 1/Analise Inferencial de Dados/Analise_Descritiva_CTI.ipynb` |

## Entrega 2
<br><br>

### Módulo do painel financeiro

| **Aluno(s) Responsável(veis)** | Mauricio Suster (uso da ferramenta), com Bruno Nobrega, Kaio Inglez e Yuri Santana |
| :--- | :--- |
| **Ferramenta utilizada** | Claude (Anthropic) |
| **Versão/modelo** | Claude Opus 5.5 |
| **Disciplina / Trabalho** | Contabilidade e Finanças – Entrega 2: painel financeiro em Streamlit |
| **Finalidade de uso** | Geração do código do painel (KPIs, índices da DFC, capital de giro, fluxo de caixa e DVA), do script de preparação dos dados do painel e do teste que compara o painel com a planilha da entrega. Ajustes pedidos pelo grupo: retirada de itens fora do pedido do professor, nomes das abas e leitura no modo escuro. |
| ***Prompts* principais utilizados** | 1. Inclua no painel financeiro as análises da Entrega 2 de Contabilidade e retire os itens que não fazem parte do pedido do professor.<br>2. Corrija as cores das tabelas que ficam ilegíveis no modo escuro. |
| **Trechos ou entregas afetadas** | `src/Entrega 2/painel_financeiro` (`app.py`, `calculos.py`, `preparar_dados.py`, `testar_painel.py` e `README.md`) |


### Módulo do dashboard CTI

| **Aluno(s) Responsável(veis)** | Mauricio Suster (uso da ferramenta), com Bruno Nobrega, Kaio Inglez e Yuri Santana |
| :--- | :--- |
| **Ferramenta utilizada** | Claude (Anthropic) |
| **Versão/modelo** | Claude Opus 5.5 |
| **Disciplina / Trabalho** | PI Ciência de Dados – Entrega 2: dashboard funcional e publicado |
| **Finalidade de uso** | Geração do código do dashboard em Streamlit (leitura da base, KPIs, filtros, 7 páginas, simulador de sensibilidade e regressão), dos testes automáticos e do README com instruções de execução. |
| ***Prompts* principais utilizados** | 1. Escreva a Entrega 2 de PI Ciência de Dados: documentação, instruções de execução e código do dashboard em Streamlit com os 5 KPIs.<br>2. Amplie o dashboard para a versão final do projeto. |
| **Trechos ou entregas afetadas** | `src/Entrega 2/dashboard_cti` (`app.py`, `dados.py`, `formatos.py`, `paginas/`, `testar_dashboard.py` e `README.md`) |

### Módulo de cálculos e modelos da Entrega 2

| **Aluno(s) Responsável(veis)** | Mauricio Suster (uso da ferramenta), com Bruno Nobrega, Kaio Inglez e Yuri Santana |
| :--- | :--- |
| **Ferramenta utilizada** | Claude (Anthropic) |
| **Versão/modelo** | Claude Opus 5.5 |
| **Disciplina / Trabalho** | Contabilidade e Finanças e Análise Inferencial de Dados – Entrega 2: script de indicadores e notebook de regressão |
| **Finalidade de uso** | Geração do script que calcula fluxo de caixa, índices da DFC, capital de giro e DVA para todos os cenários, e do notebook com os modelos de regressão, diagnósticos e validação. |
| ***Prompts* principais utilizados** | 1. Elabore a Entrega 2 de Contabilidade e Finanças com índices da DFC, capital de giro, fluxo de caixa e DVA, junto com os KPIs.<br>2. Elabore a Entrega 2 de Análise Inferencial: regressão em notebook, com interpretação dos coeficientes, diagnósticos, limitações e relatório técnico. |
| **Trechos ou entregas afetadas** | `Documentos/Entrega 2/Contabilidade e Finanças/calculo_entrega2.py` e `Documentos/Entrega 2/Analise Inferencial de Dados/Analise_Regressao_CTI.ipynb` |

## Apoio ao longo do projeto
<br><br>

### Módulo de apoio (conceitos, revisão e correção de erros)

| **Aluno(s) Responsável(veis)** | Bruno Nobrega, Kaio Inglez, Mauricio Suster e Yuri Santana |
| :--- | :--- |
| **Ferramenta utilizada** | Claude (Anthropic) |
| **Versão/modelo** | Claude Opus 5.5 |
| **Disciplina / Trabalho** | Projeto Interdisciplinar – PI Ciência de Dados, Contabilidade e Finanças, Análise Inferencial de Dados e Engenharia de Software e Arquitetura de Sistemas |
| **Finalidade de uso** | Explicação de conceitos (KPIs, DFC, capital de giro, regressão e UML), revisão de código e de fórmulas, ajuda para corrigir erros de execução e revisão de ortografia e clareza dos textos. Cada sugestão foi conferida pelo grupo antes de ser usada. |
| ***Prompts* principais utilizados** | 1. Explique boas práticas em pandas para limpar e padronizar um CSV com separador ";", codificação latin1 e números no formato brasileiro.<br>2. Revise este trecho do nosso notebook de preparação e aponte erros ou riscos de perda de dados: [código]<br>3. Confira se estas fórmulas do nosso dicionário de KPIs estão corretas e batem com a planilha: [tabela]<br>4. Explique como montar a DFC pelos métodos direto e indireto e como calcular NCG, saldo de tesouraria e a classificação de Fleuriet.<br>5. Quais diagnósticos devemos apresentar numa regressão linear e como interpretar Breusch-Pagan e Jarque-Bera?<br>6. Revise a descrição dos nossos diagramas de casos de uso e de implantação e aponte erros de notação UML: [texto]<br>7. Este erro aparece ao rodar o dashboard. Explique a causa e como corrigir: [mensagem de erro]<br>8. Revise a ortografia e a clareza deste trecho do relatório, sem mudar o conteúdo: [texto] |
| **Trechos ou entregas afetadas** | – Função de limpeza dos dados do notebook de preparação (seção 5), ajustada após a revisão;<br>– Correção do erro de execução do dashboard (arquivo `app.py`);<br>– Revisão de ortografia da introdução e da conclusão do relatório. |

***Declaro que o uso acima descrito está em conformidade com o GUIA PARA O USO RESPONSÁVEL DE
INTELIGÊNCIA ARTIFICIAL NA FECAP e que o conteúdo final é de minha plena responsabilidade
autoral.***

**Data:** 09/11/2026

> **Observação:** a inclusão da Declaração de Uso de IA é obrigatória em atividades avaliativas oficiais (NI1, NI2, Prova Oficial) e trabalhos de conclusão de curso (Art. 6º, parágrafo único). A delegação de redação a ferramentas de IA sem declaração é equiparada a plágio (Art. 5º).