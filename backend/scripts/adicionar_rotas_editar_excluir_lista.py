from pathlib import Path

path = Path(r".\app\api\routes.py")
text = path.read_text(encoding="utf-8")

if '@router.put("/listas/{lista_id}")' not in text:
    bloco = '''

@router.put("/listas/{lista_id}", response_model=ListaCompraRead)
def atualizar_lista(
    lista_id: int,
    payload: dict,
    db: Session = Depends(get_db)
):
    item = db.query(ListaCompra).filter(ListaCompra.id == lista_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Lista nao encontrada")

    nome = payload.get("nome")
    if nome:
        item.nome = nome

    db.commit()
    db.refresh(item)
    return item


@router.delete("/listas/{lista_id}")
def deletar_lista(
    lista_id: int,
    db: Session = Depends(get_db)
):
    item = db.query(ListaCompra).filter(ListaCompra.id == lista_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Lista nao encontrada")

    db.query(ItemListaCompra).filter(ItemListaCompra.lista_id == lista_id).delete()
    db.delete(item)
    db.commit()

    return {"ok": True, "message": "Lista removida com sucesso"}

'''
    text += bloco

path.write_text(text, encoding="utf-8")
print("Rotas PUT/DELETE de listas adicionadas.")
