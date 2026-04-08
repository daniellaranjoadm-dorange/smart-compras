# -*- coding: utf-8 -*-
from pathlib import Path

path = Path(r".\app\routes\cesta.py")
content = path.read_text(encoding="utf-8")

# =========================
# ADICIONAR FILTRO INTELIGENTE POR BASE
# =========================
old = '''        assinatura, base, medida_valor, medida_unidade = dados_assinatura_do_produto(produto)      

        if medida_valor is None:
            continue
'''

new = '''        assinatura, base, medida_valor, medida_unidade = dados_assinatura_do_produto(produto)

        if not base:
            continue

        # filtro semântico (CORE DO MATCHING)
        termo_norm = termo.lower()
        if termo_norm not in base.lower():
            continue

        if medida_valor is None:
            continue
'''

if old not in content:
    raise SystemExit("Bloco alvo nao encontrado (matching base)")

content = content.replace(old, new)

path.write_text(content, encoding="utf-8", newline="\n")

print("PATCH_MATCHING_BASE_OK")
