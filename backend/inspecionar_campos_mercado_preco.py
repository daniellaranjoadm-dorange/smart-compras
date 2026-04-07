from pathlib import Path

path = Path("app/models/entities.py")
lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()

targets = [
    "class RedeMercado",
    "class UnidadeMercado",
    "class PrecoProduto",
    "class Preco",
    "class Produto",
    "class Cidade",
]

for idx, line in enumerate(lines):
    if any(t in line for t in targets):
        print(f"\n=== trecho a partir da linha {idx+1} ===")
        for j in range(idx, min(idx + 35, len(lines))):
            print(f"{j+1}: {lines[j]}")
