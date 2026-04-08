# -*- coding: utf-8 -*-
from pathlib import Path

path = Path(r".\app\routes\cesta.py")
content = path.read_text(encoding="utf-8")

start = content.index("def ofertas_para_item(db: Session, termo: str, categoria: str | None):")
end = content.index('@router.get("")')

novo_bloco = '''def ofertas_para_item(db: Session, termo: str, categoria: str | None):
    termo_norm = normalizar(termo).strip()

    consulta = db.query(Produto, Categoria).outerjoin(Categoria, Produto.categoria_id == Categoria.id)

    if categoria:
        consulta = consulta.filter(Categoria.nome == categoria)

    produtos_encontrados = consulta.order_by(Produto.nome.asc()).limit(5000).all()

    ofertas = []

    for produto, categoria_obj in produtos_encontrados:
        if produto_bloqueado(produto.nome):
            continue

        assinatura, base, medida_valor, medida_unidade = dados_assinatura_do_produto(produto)

        if not assinatura or not base:
            continue

        base_norm = normalizar(base).strip()

        # matching semântico exato por base
        if base_norm != termo_norm:
            continue

        if medida_valor is None or not medida_unidade:
            continue

        precos_raw = (
            db.query(PrecoProduto, UnidadeMercado, RedeMercado, Cidade)
            .join(UnidadeMercado, PrecoProduto.unidade_id == UnidadeMercado.id)
            .join(RedeMercado, UnidadeMercado.rede_id == RedeMercado.id)
            .join(Cidade, UnidadeMercado.cidade_id == Cidade.id)
            .filter(PrecoProduto.produto_id == produto.id)
            .all()
        )

        for preco, unidade, rede, cidade in precos_raw:
            valor = float(preco.preco)
            if valor <= 0:
                continue

            ofertas.append({
                "query_item": termo,
                "assinatura": assinatura,
                "base": base,
                "medida_valor": medida_valor,
                "medida_unidade": medida_unidade,
                "categoria": categoria_obj.nome if categoria_obj else None,
                "produto_id": produto.id,
                "produto_nome": produto.nome,
                "preco": valor,
                "unidade_id": unidade.id,
                "unidade_nome": unidade.nome,
                "rede": rede.nome,
                "cidade": cidade.nome
            })

    ofertas = sorted(
        ofertas,
        key=lambda x: (
            -score_relevancia_item(
                x.get("base"),
                x.get("medida_valor"),
                x.get("medida_unidade"),
            ),
            x["preco"],
        )
    )

    return ofertas


'''

content = content[:start] + novo_bloco + content[end:]

path.write_text(content, encoding="utf-8", newline="\n")

print("REWRITE_OFERTAS_PARA_ITEM_OK")
