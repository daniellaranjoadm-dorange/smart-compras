from pathlib import Path

file = Path("app/web/index.html")
text = file.read_text(encoding="utf-8")

# esconder blocos de debug
text = text.replace(
    'id="produtosOutput"',
    'id="produtosOutput" style="display:none;"'
)

text = text.replace(
    'id="cidadesOutput"',
    'id="cidadesOutput" style="display:none;"'
)

file.write_text(text, encoding="utf-8")
print("OK: debug ocultado")
