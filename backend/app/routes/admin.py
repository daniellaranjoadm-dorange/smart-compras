from fastapi import APIRouter
from sqlalchemy import text

from app.db.base import engine

router = APIRouter(tags=["admin"])


@router.get("/admin/fix-db")
def fix_db():
    with engine.begin() as conn:
        result = conn.execute(text("PRAGMA table_info(usuarios);"))
        colunas = [row[1] for row in result]

        if "senha_hash" not in colunas:
            conn.execute(text("ALTER TABLE usuarios ADD COLUMN senha_hash TEXT"))

    return {"status": "ok", "message": "senha_hash garantida"}
