# -*- coding: utf-8 -*-
path = r".\scripts\importar_atacadao.py"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = '''def backend_create_product(name: str):
    payload = {"nome": name}
    resp = requests.post(f"{BACKEND_URL}/api/produtos", json=payload, timeout=30)
'''

new = '''def backend_create_product(name: str, assinatura: str | None = None):
    payload = {
        "nome": name,
        "assinatura": assinatura,
    }
    resp = requests.post(f"{BACKEND_URL}/api/produtos", json=payload, timeout=30)
'''

content = content.replace(old, new)

old2 = '''def backend_get_or_create_product(name: str):
    found_id = backend_find_product_id_by_name(name)
    if found_id:
        return found_id, False

    created_id = backend_create_product(name)
    return created_id, True
'''

new2 = '''def backend_get_or_create_product(name: str, assinatura: str | None = None):
    found_id = backend_find_product_id_by_name(name)
    if found_id:
        return found_id, False

    created_id = backend_create_product(name, assinatura=assinatura)
    return created_id, True
'''

content = content.replace(old2, new2)

old3 = '''                    produto_id, created = backend_get_or_create_product(name)
'''

new3 = '''                    produto_id, created = backend_get_or_create_product(name, assinatura=assinatura)
'''

content = content.replace(old3, new3)

with open(path, "w", encoding="utf-8", newline="\n") as f:
    f.write(content)

print("IMPORTER_PATCH_OK")
