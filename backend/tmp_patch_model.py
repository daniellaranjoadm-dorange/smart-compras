# -*- coding: utf-8 -*-
path = r".\app\models\entities.py"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

target = '''class Produto(Base):
    __tablename__ = "produtos"'''

if 'assinatura: Mapped[str | None] = mapped_column(nullable=True, index=True)' not in content:
    if target in content:
        content = content.replace(
            target,
            target
        )
        content = content.replace(
            'categoria_id',
            'categoria_id\n    assinatura: Mapped[str | None] = mapped_column(nullable=True, index=True)',
            1
        )

with open(path, "w", encoding="utf-8", newline="\n") as f:
    f.write(content)

print("MODEL_PATCH_OK")
