from app.db.base import SessionLocal
from app.models.entities import Produto

db = SessionLocal()

produtos = [
    "Arroz",
    "Feijão",
    "Leite",
    "Café",
    "Açúcar",
    "Óleo",
    "Macarrão",
    "Sal",
    "Farinha",
    "Manteiga",
]

existentes = {p.nome for p in db.query(Produto).all()}

novos = 0
for nome in produtos:
    if nome not in existentes:
        db.add(Produto(nome=nome))
        novos += 1

db.commit()
db.close()

print(f"OK: seed de produtos concluido. Novos produtos: {novos}")
