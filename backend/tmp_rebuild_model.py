# -*- coding: utf-8 -*-
import re

path = r".\app\models\entities.py"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Corrigir bloco quebrado do Produto
pattern = r'class Produto\(Base\):.*?class'
match = re.search(pattern, content, re.DOTALL)

if not match:
    raise SystemExit("Classe Produto não encontrada")

bloco = match.group(0)

# reconstruir corretamente
bloco_corrigido = bloco

# remove linhas quebradas de categoria_id
bloco_corrigido = re.sub(r'\n\s*categoria_id\s*\n', '\n', bloco_corrigido)

# garante categoria_id correto
if 'categoria_id:' not in bloco_corrigido:
    bloco_corrigido = bloco_corrigido.replace(
        'nome:',
        'nome:\n    categoria_id: Mapped[int | None] = mapped_column(ForeignKey("categorias.id"), nullable=True)'
    )

# garante assinatura
if 'assinatura:' not in bloco_corrigido:
    bloco_corrigido = bloco_corrigido.replace(
        'categoria_id: Mapped[int | None] = mapped_column(ForeignKey("categorias.id"), nullable=True)',
        'categoria_id: Mapped[int | None] = mapped_column(ForeignKey("categorias.id"), nullable=True)\n    assinatura: Mapped[str | None] = mapped_column(nullable=True, index=True)'
    )

# substituir no arquivo
content = content.replace(bloco, bloco_corrigido)

with open(path, "w", encoding="utf-8", newline="\n") as f:
    f.write(content)

print("MODEL_REBUILD_OK")
