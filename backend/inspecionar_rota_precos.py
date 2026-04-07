from pathlib import Path

path = Path("app/api/routes.py")
lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()

for idx, line in enumerate(lines):
    if '@router.post("/precos"' in line or 'def criar_preco' in line or 'def criar_preco_produto' in line:
        print(f"\n=== trecho a partir da linha {idx+1} ===")
        for j in range(idx, min(idx + 60, len(lines))):
            print(f"{j+1}: {lines[j]}")
