from app.db.base import SessionLocal
from app.models.entities import Produto, Cidade, Mercado, Preco

db = SessionLocal()

cidade = db.query(Cidade).first()
produtos = db.query(Produto).all()

if not cidade or not produtos:
    print("ERRO: precisa ter cidade e produtos")
    exit()

# criar mercados
mercados_nomes = ["Mercado A", "Mercado B", "Mercado C"]

mercados = []
for nome in mercados_nomes:
    m = db.query(Mercado).filter_by(nome=nome).first()
    if not m:
        m = Mercado(nome=nome, cidade_id=cidade.id)
        db.add(m)
        db.commit()
        db.refresh(m)
    mercados.append(m)

print(f"OK: mercados: {[m.nome for m in mercados]}")

# criar preços
import random

count = 0

for produto in produtos:
    for mercado in mercados:
        preco_existente = db.query(Preco).filter_by(
            produto_id=produto.id,
            mercado_id=mercado.id
        ).first()

        if not preco_existente:
            preco = round(random.uniform(3.0, 20.0), 2)

            db.add(Preco(
                produto_id=produto.id,
                mercado_id=mercado.id,
                preco=preco
            ))
            count += 1

db.commit()
db.close()

print(f"OK: preços criados: {count}")
