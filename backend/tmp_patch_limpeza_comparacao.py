# -*- coding: utf-8 -*-
from pathlib import Path

path = Path(r".\app\routes\comparacao.py")
content = path.read_text(encoding="utf-8")

old = '''        if not assinatura or not base:
            continue
'''

new = '''        if not assinatura or not base:
            continue

        # BLOQUEIO PRODUTOS SEM MEDIDA (CRÍTICO)
        if medida_valor is None or not medida_unidade:
            continue

        # BLOQUEIO ASSINATURA LIXO
        if assinatura.endswith("_na"):
            continue
'''

if old not in content:
    raise SystemExit("Bloco base nao encontrado para limpeza.")

content = content.replace(old, new)

path.write_text(content, encoding="utf-8", newline="\n")

print("PATCH_LIMPEZA_COMPARACAO_OK")
