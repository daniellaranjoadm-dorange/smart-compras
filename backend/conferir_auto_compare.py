from pathlib import Path

path = Path("app/web/smart-comparacao.js")
lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()

for i, line in enumerate(lines, 1):
    if (
        "currentComparacaoTab" in line
        or "runActiveComparacao" in line
        or 'addEventListener("change"' in line
        or "Erro no auto compare" in line
    ):
        print(f"{i}: {line}")
