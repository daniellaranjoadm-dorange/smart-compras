from pathlib import Path

file = Path("app/web/index.html")
html = file.read_text(encoding="utf-8")

html = html.replace(
"""async function loadCurrentUser() {""",
"""async function loadCurrentUser() {
  setStatus("Carregando...");
"""
)

html = html.replace(
"""return data;""",
"""setStatus("Autenticado como " + data.nome, "ok");
return data;"""
)

html = html.replace(
"""return null;""",
"""setStatus("Nao autenticado");
return null;"""
)

file.write_text(html, encoding="utf-8")
print("OK: loadCurrentUser estabilizado")
