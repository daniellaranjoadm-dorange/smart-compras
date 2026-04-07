import json
from pathlib import Path
from decimal import Decimal

import requests
from dotenv import dotenv_values

from app.db.base import SessionLocal
from app.models.entities import Produto, Cidade, RedeMercado, UnidadeMercado, PrecoProduto

env = {str(k).lstrip("\ufeff"): v for k, v in dotenv_values(".env.stok").items()}

AUTH = env.get("STOK_AUTH_BEARER", "").strip()
SESSAO = env.get("STOK_SESSAO_ID", "").strip()
ORG = env.get("STOK_ORGANIZATION_ID", "130").strip()
DOMAIN = env.get("STOK_DOMAIN_KEY", "stokonline.com.br").strip()

if not AUTH or not SESSAO:
    print("ERRO: .env.stok incompleto")
    raise SystemExit(1)

NOME_REDE = "Stok"
NOME_UNIDADE = "Stok Rio Grande"
CIDADE_NOME = "Rio Grande"

headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {AUTH}",
    "Content-Type": "application/json",
    "domainKey": DOMAIN,
    "organizationid": ORG,
    "Origin": "https://www.stokonline.com.br",
    "Referer": "https://www.stokonline.com.br/",
    "sessao-id": SESSAO,
    "User-Agent": "Mozilla/5.0",
}

vitrines = json.loads(Path("stok_vitrines_validas.json").read_text(encoding="utf-8"))

db = SessionLocal()

cidade = db.query(Cidade).filter(Cidade.nome.ilike(CIDADE_NOME)).first()
if not cidade:
    raise Exception(f"Cidade não encontrada: {CIDADE_NOME}")

rede = db.query(RedeMercado).filter_by(nome=NOME_REDE).first()
if not rede:
    rede = RedeMercado(nome=NOME_REDE)
    db.add(rede)
    db.commit()
    db.refresh(rede)

unidade = db.query(UnidadeMercado).filter(UnidadeMercado.nome.ilike(f"%{NOME_UNIDADE}%")).first()
if not unidade:
    unidade = UnidadeMercado(
        nome=NOME_UNIDADE,
        cidade_id=cidade.id,
        rede_id=rede.id
    )
    db.add(unidade)
    db.commit()
    db.refresh(unidade)

def upsert_item(item):
    nome = (item.get("descricao") or "").strip()
    if not nome:
        return 0

    preco = item.get("preco")
    oferta = item.get("oferta") or {}
    if oferta and oferta.get("preco_oferta"):
        preco = oferta.get("preco_oferta")

    try:
        preco = Decimal(str(preco))
    except:
        return 0

    produto = db.query(Produto).filter(Produto.nome.ilike(nome)).first()
    if not produto:
        produto = db.query(Produto).filter(Produto.nome.ilike(f"%{nome[:20]}%")).first()

    if not produto:
        produto = Produto(nome=nome)
        db.add(produto)
        db.commit()
        db.refresh(produto)

    from sqlalchemy.exc import IntegrityError

    preco_obj = db.query(PrecoProduto).filter_by(
        produto_id=produto.id,
        unidade_id=unidade.id
    ).first()

    if not preco_obj:
        try:
            preco_obj = PrecoProduto(
                produto_id=produto.id,
                unidade_id=unidade.id,
                preco=preco
            )
            db.add(preco_obj)
            db.flush()  # força insert antes do commit
        except IntegrityError:
            db.rollback()
            preco_obj = db.query(PrecoProduto).filter_by(
                produto_id=produto.id,
                unidade_id=unidade.id
            ).first()
            if preco_obj:
                preco_obj.preco = preco
    else:
        preco_obj.preco = preco

    return 1

total_importados = 0

for vitrine_id, status, total_items in vitrines:
    print(f"\n=== VITRINE {vitrine_id} | total_items={total_items} ===")

    total_pages = max(1, (int(total_items) + 9) // 10)

    for page in range(1, total_pages + 1):
        url = f"https://services.vipcommerce.com.br/api-admin/v1/org/130/filial/1/centro_distribuicao/2/loja/vitrines/produtos?vitrine_ids={vitrine_id}&page={page}&limit=10"
        resp = requests.get(url, headers=headers, timeout=30)
        data = resp.json()

        items = data.get("data", [])
        print(f"pagina={page} itens={len(items)}")

        for item in items:
            total_importados += upsert_item(item)

        db.commit()

db.close()

print(f"\nOK: importação completa finalizada. Itens importados/atualizados: {total_importados}")
