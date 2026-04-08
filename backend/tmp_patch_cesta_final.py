# -*- coding: utf-8 -*-
from pathlib import Path

path = Path(r".\app\routes\cesta.py")
content = path.read_text(encoding="utf-8")

# =========================
# REMOVER FILTRO BURRO
# =========================
content = content.replace(
'''        if tokens_q and not all(token in nome_norm for token in tokens_q):
            continue
''',
''
)

# =========================
# TROCAR SORT PRINCIPAL
# =========================
content = content.replace(
'''    ofertas = sorted(ofertas, key=lambda x: x["preco"])''',
'''    ofertas = sorted(
        ofertas,
        key=lambda x: (
            -score_relevancia_item(
                x.get("base"),
                x.get("medida_valor"),
                x.get("medida_unidade"),
            ),
            x["preco"],
        )
    )'''
)

path.write_text(content, encoding="utf-8", newline="\n")

print("PATCH_CESTA_FINAL_OK")
