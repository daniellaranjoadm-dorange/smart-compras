from pathlib import Path

path = Path(r".\app\api\routes.py")
text = path.read_text(encoding="utf-8")

# remove qualquer 1=1 inválido
text = text.replace("1=1", "True")

# garantir import correto
if "from sqlalchemy import true" not in text:
    text = text.replace(
        "from sqlalchemy.orm import Session",
        "from sqlalchemy.orm import Session\nfrom sqlalchemy import true"
    )

path.write_text(text, encoding="utf-8")
print("Corrigido: 1=1 removido.")
