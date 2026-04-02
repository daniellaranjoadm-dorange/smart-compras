from pathlib import Path

file = Path("app/api/routes.py")
text = file.read_text(encoding="utf-8")

text = text.replace(
"""@router.post("/itens", response_model=ItemListaCompraRead)
def criar_item(payload: ItemListaCompraCreate, db: Session = Depends(get_db)):
    item = ItemListaCompra(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item""",
"""@router.post("/itens", response_model=ItemListaCompraRead)
def criar_item(
    payload: ItemListaCompraCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    lista = db.query(ListaCompra).filter(
        ListaCompra.id == payload.lista_id,
        ListaCompra.usuario_id == usuario.id
    ).first()

    if not lista:
        raise HTTPException(status_code=404, detail="Lista nao encontrada")

    item = ItemListaCompra(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item"""
)

text = text.replace(
"""@router.get("/itens", response_model=list[ItemListaCompraRead])
def listar_itens(db: Session = Depends(get_db)):
    return db.query(ItemListaCompra).all()""",
"""@router.get("/itens", response_model=list[ItemListaCompraRead])
def listar_itens(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    return db.query(ItemListaCompra).join(
        ListaCompra, ItemListaCompra.lista_id == ListaCompra.id
    ).filter(
        ListaCompra.usuario_id == usuario.id
    ).all()"""
)

text = text.replace(
"""@router.get("/comparacao/cidade/{cidade_id}/lista/{lista_id}", response_model=ComparacaoCidadeResponse)
def comparar_por_cidade(cidade_id: int, lista_id: int, db: Session = Depends(get_db)):
    resultado = comparar_lista_por_cidade(db, lista_id, cidade_id)
    if not resultado["lista_nome"]:
        raise HTTPException(status_code=404, detail="Lista nao encontrada.")
    return resultado""",
"""@router.get("/comparacao/cidade/{cidade_id}/lista/{lista_id}", response_model=ComparacaoCidadeResponse)
def comparar_por_cidade(
    cidade_id: int,
    lista_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    lista = db.query(ListaCompra).filter(
        ListaCompra.id == lista_id,
        ListaCompra.usuario_id == usuario.id
    ).first()

    if not lista:
        raise HTTPException(status_code=404, detail="Lista nao encontrada.")

    resultado = comparar_lista_por_cidade(db, lista_id, cidade_id)
    if not resultado["lista_nome"]:
        raise HTTPException(status_code=404, detail="Lista nao encontrada.")
    return resultado"""
)

text = text.replace(
"""@router.get("/comparacao/cidade/{cidade_id}/lista/{lista_id}/otimizada", response_model=ComparacaoCidadeOtimizadaResponse)
def comparar_por_cidade_otimizada(cidade_id: int, lista_id: int, db: Session = Depends(get_db)):
    resultado = comparar_lista_otimizada_por_cidade(db, lista_id, cidade_id)
    if not resultado["lista_nome"]:
        raise HTTPException(status_code=404, detail="Lista nao encontrada.")
    return resultado""",
"""@router.get("/comparacao/cidade/{cidade_id}/lista/{lista_id}/otimizada", response_model=ComparacaoCidadeOtimizadaResponse)
def comparar_por_cidade_otimizada(
    cidade_id: int,
    lista_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    lista = db.query(ListaCompra).filter(
        ListaCompra.id == lista_id,
        ListaCompra.usuario_id == usuario.id
    ).first()

    if not lista:
        raise HTTPException(status_code=404, detail="Lista nao encontrada.")

    resultado = comparar_lista_otimizada_por_cidade(db, lista_id, cidade_id)
    if not resultado["lista_nome"]:
        raise HTTPException(status_code=404, detail="Lista nao encontrada.")
    return resultado"""
)

text = text.replace(
"""@router.get("/resumo/cidade/{cidade_id}/lista/{lista_id}", response_model=ResumoInteligenteResponse)
def resumo_inteligente(cidade_id: int, lista_id: int, db: Session = Depends(get_db)):
    resultado = gerar_resumo_inteligente_compra(db, lista_id, cidade_id)
    if not resultado:
        raise HTTPException(status_code=404, detail="Lista nao encontrada.")
    return resultado""",
"""@router.get("/resumo/cidade/{cidade_id}/lista/{lista_id}", response_model=ResumoInteligenteResponse)
def resumo_inteligente(
    cidade_id: int,
    lista_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    lista = db.query(ListaCompra).filter(
        ListaCompra.id == lista_id,
        ListaCompra.usuario_id == usuario.id
    ).first()

    if not lista:
        raise HTTPException(status_code=404, detail="Lista nao encontrada.")

    resultado = gerar_resumo_inteligente_compra(db, lista_id, cidade_id)
    if not resultado:
        raise HTTPException(status_code=404, detail="Lista nao encontrada.")
    return resultado"""
)

file.write_text(text, encoding="utf-8")
print("OK: itens e comparacoes protegidos por usuario")
