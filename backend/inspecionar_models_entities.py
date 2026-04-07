from pathlib import Path

path = Path("app/models/entities.py")
text = path.read_text(encoding="utf-8", errors="ignore")

print("=== classes em app/models/entities.py ===")
for i, line in enumerate(text.splitlines(), 1):
    if line.strip().startswith("class "):
        print(f"{i}: {line}")
