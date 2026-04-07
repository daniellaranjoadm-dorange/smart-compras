from app.db.base import SessionLocal
from app.models.entities import Cidade

db = SessionLocal()

cidades = [
    "São Paulo",
    "Rio de Janeiro",
    "Belo Horizonte",
    "Campinas",
    "Curitiba",
]

existentes = {c.nome for c in db.query(Cidade).all()}

novas = 0
for nome in cidades:
    if nome not in existentes:
        db.add(Cidade(nome=nome))
        novas += 1

db.commit()
db.close()

print(f"OK: seed de cidades concluido. Novas cidades: {novas}")
