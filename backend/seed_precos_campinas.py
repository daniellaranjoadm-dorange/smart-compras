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

# pegar Campinas (id=2)
cidade = db.query(Cidade).filter_by(nome="Campinas").first()
produtos = db.query(Produto).all()
redes = db.query(RedeMercado).all()

if not cidade:
    print("ERRO: cidade Campinas nao encontrada")
    exit()

print("Cidade:", cidade.nome, cidade.id)

# criar unidades em Campinas
unidades = []

for rede in redes:
    nome_unidade = f"{rede.nome} - Campinas"

    u = db.query(UnidadeMercado).filter_by(
        nome=nome_unidade,
        cidade_id=cidade.id
    ).first()

    if not u:
        u = UnidadeMercado(
            nome=nome_unidade,
            cidade_id=cidade.id,
            rede_id=rede.id,
            endereco="Centro Campinas",
            cep="13000-000"
        )
        db.add(u)
        db.commit()
        db.refresh(u)

    unidades.append(u)

print("Unidades Campinas:", len(unidades))

# criar preços
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

print("OK: preços Campinas criados:", count)
