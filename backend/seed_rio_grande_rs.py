from app.db.base import SessionLocal
from app.models.entities import Estado, Cidade

db = SessionLocal()

# garantir estado RS
estado = db.query(Estado).filter_by(uf="RS").first()
if not estado:
    estado = Estado(nome="Rio Grande do Sul", uf="RS")
    db.add(estado)
    db.commit()
    db.refresh(estado)
    print("OK: estado RS criado")
else:
    print("OK: estado RS já existe")

# garantir cidade Rio Grande
cidade = db.query(Cidade).filter_by(nome="Rio Grande", estado_id=estado.id).first()
if not cidade:
    cidade = Cidade(nome="Rio Grande", estado_id=estado.id)
    db.add(cidade)
    db.commit()
    db.refresh(cidade)
    print("OK: cidade Rio Grande criada")
else:
    print("OK: cidade Rio Grande já existe")

print("ESTADO_ID:", estado.id)
print("CIDADE_ID:", cidade.id)

db.close()
