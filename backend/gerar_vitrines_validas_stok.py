import json
from pathlib import Path

rows = json.loads(Path("stok_vitrines_resultado.json").read_text(encoding="utf-8"))

validas = [r for r in rows if r[1] == 200 and isinstance(r[2], int) and r[2] > 0]

print("=== VITRINES COM PRODUTOS ===")
for vitrine, status, total_items in validas:
    print(vitrine, total_items)

Path("stok_vitrines_validas.json").write_text(
    json.dumps(validas, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print("\nOK: salvo em stok_vitrines_validas.json")
