from pathlib import Path

path = Path(r".\app\api\routes.py")
text = path.read_text(encoding="utf-8")

if "from sqlalchemy import true" not in text:
    text = text.replace(
        "from sqlalchemy.orm import Session",
        "from sqlalchemy.orm import Session
from sqlalchemy import true"
    )

text = text.replace("1=1", "true()")

path.write_text(text, encoding="utf-8")
print("routes.py corrigido: 1=1 -> true()")
