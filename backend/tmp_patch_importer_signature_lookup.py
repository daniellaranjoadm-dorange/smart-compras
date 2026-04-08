# -*- coding: utf-8 -*-
path = r".\scripts\importar_atacadao.py"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

if "def backend_find_product_id_by_signature" not in content:
    anchor = '''def backend_find_product_id_by_name(name: str):
    alvo = normalize_text(name)
    produtos = backend_get_products()

    for p in produtos:
        produto_nome = p.get("nome") or p.get("name") or p.get("descricao") or ""
        if normalize_text(produto_nome) == alvo:
            return p.get("id")

    return None
'''
    insert = '''def backend_find_product_id_by_name(name: str):
    alvo = normalize_text(name)
    produtos = backend_get_products()

    for p in produtos:
        produto_nome = p.get("nome") or p.get("name") or p.get("descricao") or ""
        if normalize_text(produto_nome) == alvo:
            return p.get("id")

    return None

def backend_find_product_id_by_signature(assinatura: str | None):
    if not assinatura:
        return None

    produtos = backend_get_products()

    for p in produtos:
        assinatura_db = p.get("assinatura")
        if assinatura_db and assinatura_db == assinatura:
            return p.get("id")

    return None
'''
    content = content.replace(anchor, insert)

old = '''def backend_get_or_create_product(name: str, assinatura: str | None = None):
    found_id = backend_find_product_id_by_name(name)
    if found_id:
        return found_id, False

    created_id = backend_create_product(name, assinatura=assinatura)
    return created_id, True
'''

new = '''def backend_get_or_create_product(name: str, assinatura: str | None = None):
    found_id = backend_find_product_id_by_signature(assinatura)
    if found_id:
        return found_id, False

    found_id = backend_find_product_id_by_name(name)
    if found_id:
        return found_id, False

    created_id = backend_create_product(name, assinatura=assinatura)
    return created_id, True
'''

content = content.replace(old, new)

with open(path, "w", encoding="utf-8", newline="\n") as f:
    f.write(content)

print("IMPORTER_SIGNATURE_PATCH_OK")
