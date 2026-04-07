import json
from pathlib import Path

data = json.loads(Path("stok_api_auth_sample.json").read_text(encoding="utf-8"))

print("=== TOPO ===")
print(type(data).__name__)

if isinstance(data, dict):
    print("CHAVES:", list(data.keys())[:30])

    payload = data.get("data")
    print("\n=== DATA ===")
    print("TIPO:", type(payload).__name__)

    if isinstance(payload, list):
        print("TAMANHO:", len(payload))
        if payload:
            item0 = payload[0]
            print("TIPO_ITEM_0:", type(item0).__name__)
            if isinstance(item0, dict):
                print("CHAVES_ITEM_0:", list(item0.keys())[:80])
                print("\nITEM_0_JSON:")
                print(json.dumps(item0, ensure_ascii=False, indent=2)[:6000])

    elif isinstance(payload, dict):
        print("CHAVES_DATA:", list(payload.keys())[:80])
        print("\nDATA_JSON:")
        print(json.dumps(payload, ensure_ascii=False, indent=2)[:6000])

print("\n=== PAGINATOR ===")
paginator = data.get("paginator")
print(type(paginator).__name__)
if paginator is not None:
    print(json.dumps(paginator, ensure_ascii=False, indent=2)[:3000])
