import json
import re
from pathlib import Path

text = Path("atacadao_catalogo.json").read_text(encoding="utf-8")

matches = sorted(set(re.findall(r'https?://[^"\\s]+', text)))

print("=== URLS ENCONTRADAS ===")
for m in matches[:100]:
    print(m)
