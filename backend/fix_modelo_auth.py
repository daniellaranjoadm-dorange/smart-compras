from pathlib import Path

file = Path("app/api/routes.py")
text = file.read_text(encoding="utf-8")

text = text.replace(
"""def gerar_lista_de_modelo(lista_modelo_id: int, db: Session = Depends(get_db)): """,
"""def gerar_lista_de_modelo(
    lista_modelo_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):"""
)

text = text.replace(
"""modelo = db.query(ListaModelo).filter(ListaModelo.id == lista_modelo_id).first()""",
"""modelo = db.query(ListaModelo).filter(
    ListaModelo.id == lista_modelo_id,
    ListaModelo.usuario_id == usuario.id
).first()"""
)

file.write_text(text, encoding="utf-8")
print("OK: geracao protegida")
