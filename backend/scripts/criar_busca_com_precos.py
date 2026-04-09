from pathlib import Path

path = Path(r".\app\api\routes.py")
code = path.read_text(encoding="utf-8")

bloco = '''

@router.get("/produtos/busca-com-precos")
def buscar_produtos_com_precos(termo: str, db: Session = Depends(get_db)):
    termo = (termo or "").strip()

    if len(termo) < 2:
        return []

    produtos = (
        db.query(Produto)
        .filter(Produto.nome.ilike(f"%{termo}%"))
        .order_by(Produto.nome.asc())
        .limit(8)
        .all()
    )

    resultado = []

    for produto in produtos:
        melhor_preco = (
            db.query(PrecoProduto, UnidadeMercado)
            .join(UnidadeMercado, PrecoProduto.unidade_id == UnidadeMercado.id)
            .filter(PrecoProduto.produto_id == produto.id)
            .order_by(PrecoProduto.preco.asc())
            .first()
        )

        item = {
            "id": produto.id,
            "nome": produto.nome,
            "mercado": None,
            "preco": None
        }

        if melhor_preco:
            preco_obj, unidade_obj = melhor_preco
            item["mercado"] = unidade_obj.nome
            item["preco"] = float(preco_obj.preco)

        resultado.append(item)

    return resultado
'''.strip()

if '/produtos/busca-com-precos' not in code:
    code = code.rstrip() + "\n\n" + bloco + "\n"

path.write_text(code, encoding="utf-8")
print("ENDPOINT_OK")
