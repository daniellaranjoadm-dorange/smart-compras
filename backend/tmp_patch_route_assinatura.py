# -*- coding: utf-8 -*-
path = r".\app\api\routes.py"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = '''    novo = Produto(
        nome=payload.nome,
        categoria_id=payload.categoria_id,
    )'''

new = '''    novo = Produto(
        nome=payload.nome,
        categoria_id=payload.categoria_id,
        assinatura=payload.assinatura,
    )'''

if old in content:
    content = content.replace(old, new)
else:
    print("BLOCO_CRIA_PRODUTO_NAO_ENCONTRADO")

with open(path, "w", encoding="utf-8", newline="\n") as f:
    f.write(content)

print("ROUTE_PATCH_OK")
