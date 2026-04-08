# -*- coding: utf-8 -*-
from pathlib import Path

# =========================
# 1) PATCH CERTO EM comparacao.py
# =========================
path = Path(r".\app\routes\comparacao.py")
content = path.read_text(encoding="utf-8")

old = '        if tokens_q and not all(token in nome_norm for token in tokens_q):\n            continue\n'
new = ''

if old in content:
    content = content.replace(old, new)
    print("[PATCH_OK] removido filtro legado por nome_norm em comparacao.py")
else:
    print("[AVISO] filtro legado por nome_norm nao encontrado exatamente em comparacao.py")

path.write_text(content, encoding="utf-8", newline="\n")

# =========================
# 2) INSPECAO DO CAMINHO ATIVO DA CESTA
# =========================
path_cesta = Path(r".\app\routes\cesta.py")
lines = path_cesta.read_text(encoding="utf-8").splitlines()

print("\n=== TRECHO CESTA 240-390 ===")
for i in range(239, min(390, len(lines))):
    print(f"{i+1:4}: {lines[i]}")

print("\n=== LINHAS COM PRECO/MIN/SORT ===")
for i, line in enumerate(lines, start=1):
    if (
        "preco" in line or
        ".sort(" in line or
        "sorted(" in line or
        "min(" in line or
        "melhor_mercado" in line or
        "encontrados" in line
    ):
        print(f"{i:4}: {line}")
