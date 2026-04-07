import json
from pathlib import Path

data = json.loads(Path("stok_api_auth_sample.json").read_text(encoding="utf-8"))
payload = data.get("data")

def walk(obj, path="root", depth=0, max_depth=3):
    if depth > max_depth:
        return

    if isinstance(obj, dict):
        for k, v in obj.items():
            key_lower = str(k).lower()
            if any(x in key_lower for x in [
                "nome", "name", "descricao", "description",
                "preco", "price", "valor", "sale",
                "sku", "ean", "id", "produto", "product"
            ]):
                print(f"{path}.{k} -> {type(v).__name__} -> {repr(v)[:200]}")
            walk(v, f"{path}.{k}", depth + 1, max_depth)

    elif isinstance(obj, list):
        for i, item in enumerate(obj[:2]):
            walk(item, f"{path}[{i}]", depth + 1, max_depth)

print("=== CAMPOS CANDIDATOS ===")
walk(payload)
