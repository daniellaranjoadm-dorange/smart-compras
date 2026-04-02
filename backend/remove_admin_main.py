from pathlib import Path

file = Path("app/main.py")
text = file.read_text(encoding="utf-8")

text = text.replace("from app.routes import admin
", "")
text = text.replace("app.include_router(admin.router)
", "")

file.write_text(text, encoding="utf-8")
print("OK: rota admin removida do main.py")
