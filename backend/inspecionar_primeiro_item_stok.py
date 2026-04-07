import json
from pathlib import Path

data = json.loads(Path("stok_primeira_vitrine_com_produtos.json").read_text(encoding="utf-8"))

payload = data.get("data", [])
print("TOTAL_ITENS:", len(payload))

if payload and isinstance(payload[0], dict):
    item0 = payload[0]
    print("CHAVES_ITEM_0:", list(item0.keys())[:100])
    print(json.dumps(item0, ensure_ascii=False, indent=2)[:8000])
else:
    print("Sem item 0 válido")
