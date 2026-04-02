from pathlib import Path

file = Path("app/api/routes.py")
text = file.read_text(encoding="utf-8")

# importar dependência
if "get_current_user" not in text:
    text = text.replace(
        "from app.core.security",
        "from app.core.security\nfrom app.core.deps import get_current_user"
    )

# CRIAR LISTA SEGURA
text = text.replace(
"""@router.post("/listas", response_model=ListaCompraRead)
def criar_lista(payload: ListaCompraCreate, db: Session = Depends(get_db)):
    item = ListaCompra(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item""",
"""@router.post("/listas", response_model=ListaCompraRead)
def criar_lista(
    payload: ListaCompraCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    dados = payload.model_dump()
    dados["usuario_id"] = usuario.id

    item = ListaCompra(**dados)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item"""
)

# LISTAR LISTAS SEGURA
text = text.replace(
"""@router.get("/listas", response_model=list[ListaCompraRead])
def listar_listas(db: Session = Depends(get_db), usuario_id: int | None = None):
    query = db.query(ListaCompra)
    if usuario_id is not None:
        query = query.filter(ListaCompra.usuario_id == usuario_id)
    return query.order_by(ListaCompra.nome).all()""",
"""@router.get("/listas", response_model=list[ListaCompraRead])
def listar_listas(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    return db.query(ListaCompra).filter(
        ListaCompra.usuario_id == usuario.id
    ).order_by(ListaCompra.nome).all()"""
)

file.write_text(text, encoding="utf-8")
print("OK: listas protegidas por usuario")
