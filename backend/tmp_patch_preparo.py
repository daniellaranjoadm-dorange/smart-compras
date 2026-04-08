# -*- coding: utf-8 -*-
path = r".\app\services\normalizacao_produto.py"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

novo = """

PALAVRAS_PREPARO = [
    " com ", " ao ", " aos ",
    "pronto", "pronta",
    "congelado", "congelada",
    "mistura", "tempero",
    "sabor", "molho",
    "carreteiro", "strogonoff",
    "sopinha", "refeicao"
]
"""

if "PALAVRAS_PREPARO" not in content:
    content = content.replace("EXCLUIR_LEITE =", novo + "\nEXCLUIR_LEITE =")

content = content.replace(
    "base = normalizar_nome(nome)",
    "base = normalizar_nome(nome)\n    if any(p in base for p in PALAVRAS_PREPARO): return None"
)

with open(path, "w", encoding="utf-8", newline="\n") as f:
    f.write(content)

print("PATCH_PREPARO_OK")
