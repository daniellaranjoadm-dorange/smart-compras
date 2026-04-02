from pathlib import Path

file = Path("app/web/index.html")
html = file.read_text(encoding="utf-8")

# garantir que login usa fetch normal (sem token)
html = html.replace(
    "window.SMART_AUTH.apiFetch(API_BASE + \"/auth/login\"",
    "fetch(API_BASE + \"/auth/login\""
)

# garantir que register usa fetch normal
html = html.replace(
    "window.SMART_AUTH.apiFetch(API_BASE + \"/auth/register\"",
    "fetch(API_BASE + \"/auth/register\""
)

file.write_text(html, encoding="utf-8")
print("OK: login e register corrigidos")
