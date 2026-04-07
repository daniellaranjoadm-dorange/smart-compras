from app.db.base import SessionLocal
from app.models.entities import Usuario, Produto, ListaCompra, ItemListaCompra

db = SessionLocal()

usuario = db.query(Usuario).first()
if not usuario:
    print("ERRO: nenhum usuário encontrado")
    raise SystemExit(1)

nomes_desejados = [
    "Cerveja Budweiser 473ml",
    "Açúcar Alto Alegre Refinado 1kg",
    "Café Melitta Regiões Mogiana 250g",
]

produtos = []
for nome in nomes_desejados:
    p = db.query(Produto).filter(Produto.nome.ilike(nome)).first()
    if p:
        produtos.append(p)

if not produtos:
    print("ERRO: nenhum produto alvo encontrado")
    raise SystemExit(1)

lista = ListaCompra(
    nome="Lista real Stok Rio Grande",
    usuario_id=usuario.id
)
db.add(lista)
db.commit()
db.refresh(lista)

for p in produtos:
    item = ItemListaCompra(
        lista_id=lista.id,
        produto_id=p.id,
        quantidade=1
    )
    db.add(item)

db.commit()

print("OK: lista criada")
print("LISTA_ID:", lista.id)
for p in produtos:
    print(" -", p.id, p.nome)

db.close()
