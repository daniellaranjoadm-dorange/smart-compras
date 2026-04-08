from pathlib import Path
import re

path = Path(r".\app\api\routes.py")
text = path.read_text(encoding="utf-8")

patterns = [
    (
        r'@router\.post\("/listas".*?return item\s*',
        '''@router.post("/listas", response_model=ListaCompraRead)
def criar_lista(
    payload: ListaCompraCreate,
    db: Session = Depends(get_db)
):
    dados = payload.model_dump()

    if "usuario_id" not in dados or not dados.get("usuario_id"):
        dados["usuario_id"] = 1

    item = ListaCompra(**dados)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

'''
    ),
    (
        r'@router\.get\("/listas".*?order_by\(ListaCompra\.nome\)\.all\(\)\s*',
        '''@router.get("/listas", response_model=list[ListaCompraRead])
def listar_listas(
    db: Session = Depends(get_db)
):
    return db.query(ListaCompra).order_by(ListaCompra.nome).all()

'''
    ),
    (
        r'@router\.post\("/itens".*?return item\s*',
        '''@router.post("/itens", response_model=ItemListaCompraRead)
def criar_item(
    payload: ItemListaCompraCreate,
    db: Session = Depends(get_db)
):
    lista = db.query(ListaCompra).filter(
        ListaCompra.id == payload.lista_id
    ).first()

    if not lista:
        raise HTTPException(status_code=404, detail="Lista nao encontrada")

    item = ItemListaCompra(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

'''
    ),
    (
        r'@router\.get\("/itens".*?\.all\(\)\s*',
        '''@router.get("/itens", response_model=list[ItemListaCompraRead])
def listar_itens(
    db: Session = Depends(get_db)
):
    return db.query(ItemListaCompra).all()

'''
    ),
    (
        r'@router\.delete\("/itens/\{item_id\}"\).*?return \{"ok": True, "message": "Item removido com sucesso"\}\s*',
        '''@router.delete("/itens/{item_id}")
def deletar_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(ItemListaCompra).filter(
        ItemListaCompra.id == item_id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item nao encontrado")

    db.delete(item)
    db.commit()
    return {"ok": True, "message": "Item removido com sucesso"}

'''
    ),
]

for pattern, replacement in patterns:
    text, count = re.subn(pattern, replacement, text, flags=re.S)
    print(f"Substituicoes: {count} para padrao -> {pattern[:40]}...")

path.write_text(text, encoding="utf-8")
print("routes.py corrigido com sucesso.")
