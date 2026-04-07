from app.db.base import SessionLocal
from app.models.entities import Produto, UnidadeMercado, PrecoProduto

db = SessionLocal()

unidade = db.query(UnidadeMercado).filter(UnidadeMercado.nome.ilike("%Stok Rio Grande%")).first()
if not unidade:
    print("ERRO: unidade Stok Rio Grande não encontrada")
    raise SystemExit(1)

precos = db.query(PrecoProduto).filter_by(unidade_id=unidade.id).all()

print("=== PRODUTOS COM PREÇO NO STOK ===")
for preco in precos[:30]:
    produto = db.query(Produto).filter_by(id=preco.produto_id).first()
    if produto:
        print(f"produto_id={produto.id} | {produto.nome} | preco={preco.preco}")

db.close()
