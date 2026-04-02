from pathlib import Path

file = Path("app/api/routes.py")
text = file.read_text(encoding="utf-8")

text = text.replace(
"""def listar_itens_lista_modelo(db: Session = Depends(get_db), lista_modelo_id: int | None = None):""",
"""def listar_itens_lista_modelo(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
    lista_modelo_id: int | None = None
):"""
)

text = text.replace(
"""query = db.query(ItemListaModelo)""",
"""query = db.query(ItemListaModelo).join(
    ListaModelo, ItemListaModelo.lista_modelo_id == ListaModelo.id
).filter(
    ListaModelo.usuario_id == usuario.id
)"""
)

file.write_text(text, encoding="utf-8")
print("OK: lista modelo protegida")
