from pathlib import Path

path = Path("app/web/smart-comparacao.js")
lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()

ranges = [
    (120, 260),
    (260, 380),
    (380, 470),
]

for start, end in ranges:
    print(f"\n=== linhas {start}-{end} ===")
    for i in range(start, min(end + 1, len(lines) + 1)):
        print(f"{i}: {lines[i-1]}")
