# -*- coding: utf-8 -*-
path = r".\scripts\importar_atacadao.py"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

anchor = """def backend_get_unidade_id():
    resp = requests.get(f"{BACKEND_URL}/api/unidades-mercado", timeout=30)
    resp.raise_for_status()
    data = resp.json()

    for unidade in data:
        nome = (unidade.get("nome") or "").strip().lower()
        if "atacadao" in nome and "rio grande" in nome:
            return unidade.get("id")

    raise RuntimeError("Unidade 'Atacadao Rio Grande' não encontrada em /api/unidades-mercado")
"""

insert_block = """def backend_get_existing_price_keys():
    resp = requests.get(f"{BACKEND_URL}/api/precos", timeout=60)
    resp.raise_for_status()
    data = resp.json()

    keys = set()
    for row in data:
        produto_id = row.get("produto_id")
        unidade_id = row.get("unidade_id")
        if produto_id is not None and unidade_id is not None:
            keys.add((int(produto_id), int(unidade_id)))
    return keys

"""

if insert_block not in content:
    content = content.replace(anchor, anchor + "\n\n" + insert_block)

content = content.replace(
    "    total_price_saved = 0\n",
    "    total_price_saved = 0\n    total_price_skipped = 0\n"
)

content = content.replace(
    '    unidade_id = backend_get_unidade_id()\n    log(f"[INFO] unidade_id encontrada: {unidade_id}")\n\n    seen_names = set()\n',
    '    unidade_id = backend_get_unidade_id()\n    log(f"[INFO] unidade_id encontrada: {unidade_id}")\n\n    existing_price_keys = backend_get_existing_price_keys()\n    log(f"[INFO] chaves de preço já existentes: {len(existing_price_keys)}")\n\n    seen_names = set()\n'
)

old_block = """                    total_imported += 1

                    backend_save_price(produto_id, unidade_id, price)
                    total_price_saved += 1
                    log(f"[PRECO] produto_id={produto_id} unidade_id={unidade_id} preco={price}")
"""

new_block = """                    total_imported += 1

                    price_key = (int(produto_id), int(unidade_id))
                    if price_key in existing_price_keys:
                        total_price_skipped += 1
                        log(f"[SKIP_PRECO_EXISTENTE] produto_id={produto_id} unidade_id={unidade_id}")
                        continue

                    backend_save_price(produto_id, unidade_id, price)
                    existing_price_keys.add(price_key)
                    total_price_saved += 1
                    log(f"[PRECO] produto_id={produto_id} unidade_id={unidade_id} preco={price}")
"""

if old_block not in content:
    raise SystemExit("Bloco principal de salvamento de preco nao encontrado.")

content = content.replace(old_block, new_block)

content = content.replace(
    '    log(f"Preços salvos: {total_price_saved}")\n',
    '    log(f"Preços salvos: {total_price_saved}")\n    log(f"Preços ignorados por já existirem: {total_price_skipped}")\n'
)

with open(path, "w", encoding="utf-8", newline="\n") as f:
    f.write(content)

print("PATCH_OK")
