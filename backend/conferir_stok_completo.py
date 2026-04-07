from app.db.base import SessionLocal
from app.models.entities import Produto, UnidadeMercado, PrecoProduto

db = SessionLocal()

unidade = db.query(UnidadeMercado).filter(UnidadeMercado.nome.ilike("%Stok Rio Grande%")).first()

if not unidade:
    print("ERRO: unidade Stok Rio Grande não encontrada")
    raise SystemExit(1)

precos = db.query(PrecoProduto).filter_by(unidade_id=unidade.id).all()
print("TOTAL_PRECOS_STOK:", len(precos))

print("\n=== AMOSTRA ===")
for preco in precos[:20]:
    produto = db.query(Produto).filter_by(id=preco.produto_id).first()
    print(preco.id, produto.nome if produto else preco.produto_id, preco.preco)

db.close()
