from pathlib import Path

file = Path("app/web/index.html")
html = file.read_text(encoding="utf-8")

html = html.replace(
    'id="authBox" class="row"',
    'id="authBox" class="row hidden"'
)

file.write_text(html, encoding="utf-8")
print("OK: auth escondido por padrão")
