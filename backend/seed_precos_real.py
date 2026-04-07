from app.db.base import SessionLocal
from app.models.entities import (
    Produto,
    Cidade,
    RedeMercado,
    UnidadeMercado,
    PrecoProduto,
)

import random

db = SessionLocal()

cidade = db.query(Cidade).first()
produtos = db.query(Produto).all()

if not cidade or not produtos:
    print("ERRO: precisa ter cidade e produtos")
    exit()

# =========================
# 1. REDES
# =========================
redes_nomes = ["Rede A", "Rede B", "Rede C"]
redes = []

for nome in redes_nomes:
    r = db.query(RedeMercado).filter_by(nome=nome).first()
    if not r:
        r = RedeMercado(nome=nome)
        db.add(r)
        db.commit()
        db.refresh(r)
    redes.append(r)

print("OK: redes criadas")

# =========================
# 2. UNIDADES (lojas físicas)
# =========================
unidades = []

for rede in redes:
    u = db.query(UnidadeMercado).filter_by(
        nome=f"{rede.nome} - Centro",
        cidade_id=cidade.id
    ).first()

    if not u:
        u = UnidadeMercado(
            nome=f"{rede.nome} - Centro",
            cidade_id=cidade.id,
            rede_id=rede.id,
            endereco="Centro",
            cep="00000-000"
        )
        db.add(u)
        db.commit()
        db.refresh(u)

    unidades.append(u)

print("OK: unidades criadas")

# =========================
# 3. PREÇOS
# =========================
count = 0

for produto in produtos:
    for unidade in unidades:
        existente = db.query(PrecoProduto).filter_by(
            produto_id=produto.id,
            unidade_id=unidade.id
        ).first()

        if not existente:
            preco = round(random.uniform(3.0, 20.0), 2)

            db.add(PrecoProduto(
                produto_id=produto.id,
                unidade_id=unidade.id,
                preco=preco
            ))
            count += 1

db.commit()
db.close()

print(f"OK: preços criados: {count}")
