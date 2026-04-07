from pathlib import Path

for p in Path("app").rglob("*.py"):
    text = p.read_text(encoding="utf-8", errors="ignore")
    if "comparacao" in text.lower():
        print(f"\n=== {p} ===")
        for i, line in enumerate(text.splitlines(), 1):
            if "comparacao" in line.lower() or "@router" in line.lower():
                print(f"{i}: {line}")
