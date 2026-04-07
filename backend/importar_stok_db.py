import json
from pathlib import Path
from decimal import Decimal

from app.db.base import SessionLocal
from app.models.entities import Produto, Cidade, RedeMercado, UnidadeMercado, PrecoProduto

# ===== CONFIG =====
NOME_REDE = "Stok"
NOME_UNIDADE = "Stok Rio Grande"
CIDADE_NOME = "Rio Grande"

# ===== LOAD JSON =====
data = json.loads(Path("stok_primeira_vitrine_com_produtos.json").read_text(encoding="utf-8"))
items = data.get("data", [])

print(f"Itens carregados: {len(items)}")

db = SessionLocal()

# ===== GARANTIR CIDADE =====
cidade = db.query(Cidade).filter(Cidade.nome.ilike(CIDADE_NOME)).first()
if not cidade:
    raise Exception(f"Cidade não encontrada: {CIDADE_NOME}")

# ===== GARANTIR REDE =====
rede = db.query(RedeMercado).filter_by(nome=NOME_REDE).first()
if not rede:
    rede = RedeMercado(nome=NOME_REDE)
    db.add(rede)
    db.commit()
    db.refresh(rede)
    print("Rede criada")

# ===== GARANTIR UNIDADE =====
unidade = db.query(UnidadeMercado).filter_by(nome=NOME_UNIDADE).first()
if not unidade:
    unidade = UnidadeMercado(
        nome=NOME_UNIDADE,
        cidade_id=cidade.id,
        rede_id=rede.id
    )
    db.add(unidade)
    db.commit()
    db.refresh(unidade)
    print("Unidade criada")

# ===== PROCESSAR ITENS =====
importados = 0

for item in items:
    nome = (item.get("descricao") or "").strip()
    if not nome:
        continue

    # preço
    preco = item.get("preco")
    oferta = item.get("oferta") or {}

    if oferta and oferta.get("preco_oferta"):
        preco = oferta.get("preco_oferta")

    try:
        preco = Decimal(str(preco))
    except:
        continue

    # tenta encontrar produto por nome aproximado
    produto = db.query(Produto).filter(Produto.nome.ilike(nome)).first()

    # fallback: busca parcial
    if not produto:
        produto = db.query(Produto).filter(Produto.nome.ilike(f"%{nome[:20]}%")).first()

    # se não existir, cria automaticamente
    if not produto:
        produto = Produto(nome=nome)
        db.add(produto)
        db.commit()
        db.refresh(produto)

    # upsert preço
    preco_obj = db.query(PrecoProduto).filter_by(
        produto_id=produto.id,
        unidade_id=unidade.id
    ).first()

    if not preco_obj:
        preco_obj = PrecoProduto(
            produto_id=produto.id,
            unidade_id=unidade.id,
            preco=preco
        )
        db.add(preco_obj)
    else:
        preco_obj.preco = preco

    importados += 1

db.commit()
db.close()

print(f"OK: preços importados/atualizados: {importados}")
