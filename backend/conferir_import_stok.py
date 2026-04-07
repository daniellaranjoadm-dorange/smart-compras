from app.db.base import SessionLocal
from app.models.entities import Produto, UnidadeMercado, PrecoProduto

db = SessionLocal()

print("=== ULTIMOS PRODUTOS ===")
for p in db.query(Produto).order_by(Produto.id.desc()).limit(10).all():
    print(p.id, p.nome)

print("\n=== PRECOS STOK ===")
unidade = db.query(UnidadeMercado).filter(UnidadeMercado.nome.ilike("%Stok Rio Grande%")).first()
if unidade:
    precos = db.query(PrecoProduto).filter_by(unidade_id=unidade.id).limit(20).all()
    for preco in precos:
        produto = db.query(Produto).filter_by(id=preco.produto_id).first()
        print(preco.id, produto.nome if produto else preco.produto_id, preco.preco)
else:
    print("Unidade Stok Rio Grande nao encontrada")

db.close()
