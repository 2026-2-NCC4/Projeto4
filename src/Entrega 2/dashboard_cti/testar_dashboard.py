# testar_dashboard.py
# Testes do dashboard: abre todas as páginas, confere os KPIs com as colunas da Entrega 1,
# confere o simulador e a regressão com os resultados do relatório de Análise Inferencial.
# Uso: python testar_dashboard.py

import sys

from streamlit.testing.v1 import AppTest

from dados import calcular_indicadores, carregar_base, lucro_simulado, ols

erros = []


def conferir(nome, ok, detalhe=""):
    print(f"[{'OK' if ok else 'ERRO'}] {nome} {detalhe}")
    if not ok:
        erros.append(nome)


# 1. todas as páginas abrem sem erro, com filtros diferentes
paginas = ["visao_executiva", "evolucao", "sensibilidade", "caixa", "relacoes", "qualidade", "notas"]
for pagina in paginas:
    for grupo, ano_ref in [("Todos os cenários", 11), ("Cenários 1001-1200", 12)]:
        at = AppTest.from_file("app.py", default_timeout=180)
        at.run()
        at.switch_page(f"paginas/{pagina}.py").run()
        at.sidebar.radio(key="grupo").set_value(grupo).run()
        at.sidebar.slider(key="ano_ref").set_value(ano_ref).run()
        conferir(f"página {pagina} ({grupo}, Ano {ano_ref})", not at.exception,
                 at.exception[0].value if at.exception else "")

# 2. KPIs calculados no dashboard = colunas da base da Entrega 1
d = calcular_indicadores(carregar_base())
for col in ["receita_liquida", "ebitda", "margem_ebitda", "margem_liquida", "divida_liquida"]:
    original = d[f"{col}_e1"] if f"{col}_e1" in d else d[col]
    dif = (d[col] - original).abs().max()
    conferir(f"{col} igual à Entrega 1", dif < 0.001, f"(maior diferença {dif:.6f})")

# 3. simulador sem variação devolve o lucro do arquivo
dif = max(abs(lucro_simulado(linha)["lucro_liquido"] - linha["lucro_liquido"]) for _, linha in d.sample(300, random_state=1).iterrows())
conferir("simulador sem variação = lucro do arquivo", dif < 0.01, f"(maior diferença {dif:.6f})")

# 4. regressão do Ano 6 igual à do relatório de Análise Inferencial
coef, r2, _, _ = ols(d[d["ano"] == 6], "lucro_liquido", ["receita_liquida", "custos", "grupo2"])
conferir("regressão Ano 6: coeficiente da receita 0,655", abs(coef.loc["receita_liquida", "coef"] - 0.655) < 0.001)
conferir("regressão Ano 6: coeficiente dos custos −0,542", abs(coef.loc["custos", "coef"] + 0.542) < 0.001)
conferir("regressão Ano 6: R² 0,989", abs(r2 - 0.989) < 0.001)

print(f"\n{len(erros)} erro(s)")
sys.exit(1 if erros else 0)
