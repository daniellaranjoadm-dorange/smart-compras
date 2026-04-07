import json
from pathlib import Path

data = json.loads(Path("atacadao_catalogo.json").read_text(encoding="utf-8"))

def walk(obj, path="root", depth=0, max_depth=5):
    if depth > max_depth:
        return

    if isinstance(obj, dict):
        for k, v in obj.items():
            kl = str(k).lower()
            if any(x in kl for x in [
                "slug", "catalog", "categoria", "category",
                "product", "produto", "search", "item", "id",
                "price", "preco", "offer"
            ]):
                print(f"{path}.{k} -> {type(v).__name__} -> {repr(v)[:180]}")
            walk(v, f"{path}.{k}", depth + 1, max_depth)

    elif isinstance(obj, list):
        for i, item in enumerate(obj[:5]):
            walk(item, f"{path}[{i}]", depth + 1, max_depth)

print("=== CAMPOS CANDIDATOS ===")
walk(data)
