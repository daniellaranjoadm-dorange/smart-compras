from pathlib import Path
import re

path = Path(r".\app\api\routes.py")
code = path.read_text(encoding="utf-8")

# garante import de PrecoProduto
if "PrecoProduto" not in code:
    code = code.replace(
        "from app.models.entities import ",
        "from app.models.entities import PrecoProduto, ",
        1
    )

novo_bloco = '''
@router.get("/listas/{lista_id}/resumo")
def resumo_lista(lista_id: int, db: Session = Depends(get_db)):
    itens = db.query(ItemListaCompra).filter_by(lista_id=lista_id).all()

    total_itens = len(itens)
    total_quantidade = sum(i.quantidade for i in itens)

    total_custo = 0.0

    for item in itens:
        preco_atual = (
            db.query(PrecoProduto)
            .filter(PrecoProduto.produto_id == item.produto_id)
            .order_by(PrecoProduto.id.desc())
            .first()
        )

        preco_valor = None

        if preco_atual:
            preco_valor = float(preco_atual.preco)
        else:
            historico = (
                db.query(HistoricoPreco)
                .filter(HistoricoPreco.produto_id == item.produto_id)
                .order_by(HistoricoPreco.id.desc())
                .first()
            )
            if historico:
                preco_valor = float(historico.preco)

        if preco_valor is not None:
            total_custo += preco_valor * item.quantidade

    return {
        "total_itens": total_itens,
        "total_quantidade": total_quantidade,
        "custo_estimado": round(total_custo, 2)
    }
'''.strip()

pattern = r'@router\.get\("/listas/\{lista_id\}/resumo"\)\s*def resumo_lista\(.*?(?=\n@router\.|\Z)'
match = re.search(pattern, code, flags=re.S)

if match:
    code = re.sub(pattern, novo_bloco + "\n\n", code, flags=re.S)
else:
    code = code.rstrip() + "\n\n" + novo_bloco + "\n"

path.write_text(code, encoding="utf-8")
print("PATCH_OK")
