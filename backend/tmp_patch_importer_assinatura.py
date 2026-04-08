# -*- coding: utf-8 -*-
path = r".\scripts\importar_atacadao.py"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

if 'from app.services.normalizacao_produto import gerar_assinatura_produto' not in content:
    content = content.replace(
        'import requests\n',
        'import requests\nfrom app.services.normalizacao_produto import gerar_assinatura_produto\n'
    )

old_block = """                name = extract_name(product)
                price = extract_price(product)

                if not name or price is None or price <= 0:
                    continue

                key = normalize_text(name)
                if not key or key in seen_names:
                    continue
                seen_names.add(key)

                try:
"""

new_block = """                name = extract_name(product)
                price = extract_price(product)

                if not name or price is None or price <= 0:
                    continue

                assinatura = gerar_assinatura_produto(name)
                if not assinatura:
                    log(f"[SKIP_ASSINATURA] nome='{name}'")
                    continue

                key = normalize_text(name)
                if not key or key in seen_names:
                    continue
                seen_names.add(key)

                log(f"[ASSINATURA] nome='{name}' assinatura='{assinatura}'")

                try:
"""

if old_block not in content:
    raise SystemExit("Bloco alvo nao encontrado para patch de assinatura.")

content = content.replace(old_block, new_block)

with open(path, "w", encoding="utf-8", newline="\n") as f:
    f.write(content)

print("PATCH_OK")
