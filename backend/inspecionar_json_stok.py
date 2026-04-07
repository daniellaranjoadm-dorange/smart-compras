import json
from pathlib import Path

data = json.loads(Path("stok_api_auth_sample.json").read_text(encoding="utf-8"))

print("=== TOPO ===")
if isinstance(data, dict):
    print(list(data.keys())[:50])

    for key in ["data", "items", "produtos", "results", "resultado"]:
        if key in data:
            value = data[key]
            print(f"\n=== CHAVE ENCONTRADA: {key} ===")
            print("TIPO:", type(value).__name__)
            if isinstance(value, list):
                print("TAMANHO:", len(value))
                if value and isinstance(value[0], dict):
                    print("CHAVES_ITEM_0:", list(value[0].keys())[:50])
                    print(json.dumps(value[0], ensure_ascii=False, indent=2)[:4000])
            elif isinstance(value, dict):
                print("CHAVES:", list(value.keys())[:50])
                print(json.dumps(value, ensure_ascii=False, indent=2)[:4000])
else:
    print(type(data).__name__)
    print(json.dumps(data, ensure_ascii=False, indent=2)[:4000])
