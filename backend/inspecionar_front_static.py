from pathlib import Path
import re

main_file = Path("app/main.py")
text = main_file.read_text(encoding="utf-8", errors="ignore")

print("=== app/main.py ===")
print(text)

print("\n=== HTMLs encontrados ===")
for p in Path(".").rglob("index.html"):
    if ".venv" not in str(p):
        print(p)

print("\n=== Arquivos smart-comparacao encontrados ===")
for p in Path(".").rglob("smart-comparacao.*"):
    if ".venv" not in str(p):
        print(p)
