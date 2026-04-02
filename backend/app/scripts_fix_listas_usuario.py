from sqlalchemy import text
from app.db.base import engine

with engine.begin() as conn:
    result = conn.execute(text("PRAGMA table_info(listas_compra);"))
    cols = [row[1] for row in result]

    if "usuario_id" not in cols:
        conn.execute(text("ALTER TABLE listas_compra ADD COLUMN usuario_id INTEGER"))
        print("OK: coluna usuario_id adicionada em listas_compra")
    else:
        print("OK: coluna usuario_id ja existe")
