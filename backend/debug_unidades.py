from app.db.base import SessionLocal
from app.models.entities import UnidadeMercado

db = SessionLocal()

for u in db.query(UnidadeMercado).all():
    print(u.id, u.nome, "cidade_id:", u.cidade_id)

db.close()
