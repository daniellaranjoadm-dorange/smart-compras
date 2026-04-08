# -*- coding: utf-8 -*-
path = r".\app\services\normalizacao_produto.py"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# =========================
# FIX PESO (FLOAT CORRETO)
# =========================
content = content.replace(
'r"(\d+(?:[.,]\d+)?)\s*(kg|g|ml|l)\b"',
'r"(\d+(?:[.,]\d+)?)\s*(kg|g|ml|l)\b"'
)

# =========================
# FIX CONVERSÃO (NÃO TRUNCAR)
# =========================
content = content.replace(
'valor = valor.rstrip("0").rstrip(".") if "." in valor else valor',
'valor = str(float(valor)) if "." in valor else valor'
)

# =========================
# FILTRO CONTEXTO ÓLEO
# =========================
if "EXCLUIR_OLEO_CONTEXTO" not in content:
    content = content.replace(
"EXCLUIR_OLEO = [",
"""EXCLUIR_OLEO = [
    "atum", "sardinha", "peixe", "enlatado",
    "banho", "corpo", "pele", "cosmetico", "cosmético",
"""
    )

# =========================
# BLOQUEIO EXTRA NO IF OLEO
# =========================
content = content.replace(
'if " oleo " in base:',
'''if " oleo " in base:
        # bloqueio por contexto (não alimento puro)
        if contem_algum(base, ["atum", "sardinha", "peixe"]):
            return None'''
)

with open(path, "w", encoding="utf-8", newline="\\n") as f:
    f.write(content)

print("NORMALIZACAO_PRO_PLUS_OK")
