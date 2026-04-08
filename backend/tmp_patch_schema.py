# -*- coding: utf-8 -*-
path = r".\app\schemas\entities.py"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

if "class ProdutoCreate(BaseModel):\n    assinatura: str | None = None" not in content:
    content = content.replace(
        "class ProdutoCreate(BaseModel):",
        "class ProdutoCreate(BaseModel):\n    assinatura: str | None = None"
    )

if "class ProdutoRead(ProdutoCreate):\n    assinatura: str | None = None" not in content:
    content = content.replace(
        "class ProdutoRead(ProdutoCreate):",
        "class ProdutoRead(ProdutoCreate):\n    assinatura: str | None = None"
    )

with open(path, "w", encoding="utf-8", newline="\n") as f:
    f.write(content)

print("SCHEMA_PATCH_OK")
