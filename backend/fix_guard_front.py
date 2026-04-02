from pathlib import Path

file = Path("app/web/index.html")
html = file.read_text(encoding="utf-8")

# remove o guard atual (que está bloqueando tudo)
html = html.replace(
    "document.querySelectorAll(\"form\").forEach(function(form)",
    "// GUARD REMOVIDO TEMPORARIAMENTE\n// document.querySelectorAll(\"form\").forEach(function(form)"
)

file.write_text(html, encoding="utf-8")
print("OK: bloqueio removido (login liberado)")
