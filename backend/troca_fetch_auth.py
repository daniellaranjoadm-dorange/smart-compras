from pathlib import Path
import re

file = Path("app/web/index.html")
html = file.read_text(encoding="utf-8")

html = html.replace("fetch(", "window.SMART_AUTH.apiFetch(")

file.write_text(html, encoding="utf-8")
print("OK: fetch trocado por apiFetch autenticado")
