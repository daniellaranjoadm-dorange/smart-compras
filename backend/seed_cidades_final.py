from app.db.base import SessionLocal
from app.models.entities import Cidade, Estado

db = SessionLocal()

# 1. criar estado com UF obrigatoria
estado = db.query(Estado).filter(Estado.uf == "SP").first()

if not estado:
    estado = Estado(nome="São Paulo", uf="SP")
    db.add(estado)
    db.commit()
    db.refresh(estado)
    print("OK: estado criado:", estado.id)
else:
    print("OK: estado existente:", estado.id)

# 2. criar cidades
cidades = [
    "São Paulo",
    "Campinas",
    "Santos",
    "Sorocaba",
]

existentes = {c.nome for c in db.query(Cidade).all()}

novas = 0
for nome in cidades:
    if nome not in existentes:
        db.add(Cidade(nome=nome, estado_id=estado.id))
        novas += 1

db.commit()
db.close()

print(f"OK: cidades criadas: {novas}")
