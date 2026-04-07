import json
from pathlib import Path

path = Path("stok_api_sample.json")
data = json.loads(path.read_text(encoding="utf-8"))

print("=== AMOSTRA ===")
if isinstance(data, list):
    for i, item in enumerate(data[:2], 1):
        print(f"\nITEM {i}:")
        print(json.dumps(item, ensure_ascii=False, indent=2)[:3000])
elif isinstance(data, dict):
    print(json.dumps(data, ensure_ascii=False, indent=2)[:5000])
else:
    print(type(data).__name__)
