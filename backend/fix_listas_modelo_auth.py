from pathlib import Path

file = Path("app/api/routes.py")
text = file.read_text(encoding="utf-8")

text = text.replace(
"""def listar_listas_modelo(db: Session = Depends(get_db), usuario_id: int | None = None):
    query = db.query(ListaModelo)
    if usuario_id is not None:
        query = query.filter(ListaModelo.usuario_id == usuario_id)
    return query.order_by(ListaModelo.nome).all()""",
"""def listar_listas_modelo(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    return db.query(ListaModelo).filter(
        ListaModelo.usuario_id == usuario.id
    ).order_by(ListaModelo.nome).all()"""
)

file.write_text(text, encoding="utf-8")
print("OK: listas modelo protegidas")
