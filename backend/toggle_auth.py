from pathlib import Path

file = Path("app/web/index.html")
html = file.read_text(encoding="utf-8")

html = html.replace(
"document.getElementById(\"authBox\").classList.remove(\"hidden\");",
"document.getElementById(\"authBox\").classList.remove(\"hidden\");"
)

html = html.replace(
"document.getElementById(\"authBox\").classList.add(\"hidden\");",
"document.getElementById(\"authBox\").classList.add(\"hidden\");"
)

file.write_text(html, encoding="utf-8")
print("OK: visibilidade controlada")
