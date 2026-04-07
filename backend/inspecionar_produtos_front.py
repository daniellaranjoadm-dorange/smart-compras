from pathlib import Path

path = Path("app/web/index.html")
text = path.read_text(encoding="utf-8", errors="ignore")

print("=== trechos relacionados a produtos ===")
for i, line in enumerate(text.splitlines(), 1):
    if any(x in line for x in [
        "produtos",
        "/produtos",
        "produtoSelect",
        "produto",
        "Adicionar item",
        "carregarProdutos",
    ]):
        print(f"{i}: {line}")
