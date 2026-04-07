from pathlib import Path
import re

file = Path("app/web/index.html")
text = file.read_text(encoding="utf-8")

patterns = [
    r'<h2>Produtos</h2>.*?<pre id="produtosOutput">.*?</pre>\s*</div>',
    r'<h2>Cidades</h2>.*?<pre id="cidadesOutput">.*?</pre>\s*</div>',
    r'<h2>Teste /auth/me</h2>.*?<pre id="meOutput">.*?</pre>\s*</div>',
]

changed = 0
for pattern in patterns:
    new_text, count = re.subn(
        pattern,
        '',
        text,
        flags=re.S
    )
    if count:
        text = new_text
        changed += count

file.write_text(text, encoding="utf-8")
print(f"OK: blocos de debug removidos. Alteracoes: {changed}")
