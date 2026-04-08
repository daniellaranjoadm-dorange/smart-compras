# -*- coding: utf-8 -*-
from pathlib import Path

arquivos = [
    Path(r".\app\routes\comparacao.py"),
    Path(r".\app\routes\cesta.py"),
]

for path in arquivos:
    content = path.read_text(encoding="utf-8-sig")
    path.write_text(content, encoding="utf-8", newline="\n")
    print(f"[BOM_REMOVIDO] {path}")

print("LIMPEZA_OK")
