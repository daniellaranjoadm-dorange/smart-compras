from pathlib import Path
import re

path = Path(r".\app\api\routes.py")
text = path.read_text(encoding="utf-8")

pattern = r'@router\.post\("/listas", response_model=ListaCompraRead\).*?return item\s*'
replacement = '''@router.post("/listas", response_model=ListaCompraRead)
def criar_lista(
    payload: dict,
    db: Session = Depends(get_db)
):
    nome = payload.get("nome")
    if not nome:
        raise HTTPException(status_code=400, detail="Campo nome e obrigatorio.")

    usuario_id = payload.get("usuario_id") or 1

    item = ListaCompra(
        nome=nome,
        usuario_id=usuario_id
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

'''

text, count = re.subn(pattern, replacement, text, flags=re.S)
print(f"Rotas substituidas: {count}")

path.write_text(text, encoding="utf-8")
print("criar_lista ajustada para payload simples.")
