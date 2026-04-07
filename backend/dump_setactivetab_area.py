from pathlib import Path

path = Path("app/web/smart-comparacao.js")
lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()

for start, end in [(80, 150)]:
    print(f"\n=== linhas {start}-{end} ===")
    for i in range(start, min(end + 1, len(lines) + 1)):
        print(f"{i}: {lines[i-1]}")
