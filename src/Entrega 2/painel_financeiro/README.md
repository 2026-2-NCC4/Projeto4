# Painel Financeiro – CTI Global

Contabilidade e Finanças – Entrega 02 · Projeto Interdisciplinar 4º CCOMP (FECAP)
Professor: Mauricio Lopes da Cunha · Integrantes: Bruno Nobrega, Kaio Inglez, Mauricio Suster e Yuri Santana

Painel em Streamlit com o conteúdo da pré-entrega de 30/10, junto com os KPIs:

| Aba | O que mostra |
|---|---|
| KPIs | KPIs da Entrega 1 (A03 a C08) e KPIs novos da Entrega 2 (H01 a H11) |
| 8 · Índices da DFC | Coberturas, qualidade do resultado, margem de caixa, fluxo de caixa livre |
| 9 · Capital de giro | NCG, saldo de tesouraria, CDG, modelo Fleuriet, prazos médios e ciclos |
| 10 · Fluxo de caixa | DFC pelo método direto e indireto |
| 11 · DVA | Geração e distribuição do valor adicionado |
| Notas | Fórmulas, conferências e limitações |

Os números do cenário 1 são os mesmos da `Planilha_Entrega02_Contabilidade_CTI.xlsx`.

## Arquivos

| Arquivo | Para que serve |
|---|---|
| `app.py` | O painel (telas, filtros e gráficos) |
| `calculos.py` | Lista dos indicadores e montagem das tabelas da DFC e da DVA |
| `preparar_dados.py` | Gera `dados/dados_painel.csv` a partir da saída do `calculo_entrega2.py` |
| `testar_painel.py` | Confere o painel com a planilha da Entrega 2 |
| `dados/dados_painel.csv` | Dados que o painel lê (1.200 cenários × 12 anos) |
| `requirements.txt` | Bibliotecas usadas |

## Como rodar no computador

```sh
cd "src/Entrega 2/painel_financeiro"
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

No Windows, se `python` não funcionar, use `py` no lugar (`py -m streamlit run app.py`).
O painel abre no navegador em `http://localhost:8501`.

## Como conferir com a planilha da Entrega 2

```sh
python testar_painel.py "../../../Documentos/Entrega 2/Contabilidade e Finanças/Planilha_Entrega02_Contabilidade_CTI.xlsx"
```

Resultado esperado: `864 comparações, 864 iguais, 0 diferentes`.

## Como gerar os dados de novo

O `calculo_entrega2.py` está em `Documentos/Entrega 2/Contabilidade e Finanças`.

```sh
python calculo_entrega2.py "Demonstrativo Fecap v3.csv"
python preparar_dados.py indicadores_e2_todos_cenarios.csv
```

Os dados vêm da CTI: só publicar com o repositório e o app liberados por ela.
