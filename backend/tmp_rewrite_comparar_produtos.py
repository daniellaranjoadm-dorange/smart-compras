# -*- coding: utf-8 -*-
from pathlib import Path

path = Path(r".\app\routes\comparacao.py")
content = path.read_text(encoding="utf-8")

start = content.index('@router.get("")')
end = len(content)

novo_bloco = '''@router.get("")
def comparar_produtos(
    q: str = Query(..., min_length=2),
    categoria: str | None = Query(default=None),
    limit_produtos: int = Query(default=150, le=400),
    db: Session = Depends(get_db),
):
    q_norm = normalizar(q).strip()
    tokens_q = tokens_relevantes_query(q)

    consulta = db.query(Produto, Categoria).outerjoin(Categoria, Produto.categoria_id == Categoria.id)

    if categoria:
        consulta = consulta.filter(Categoria.nome == categoria)

    produtos_encontrados = consulta.order_by(Produto.nome.asc()).limit(5000).all()

    grupos = {}

    for produto, categoria_obj in produtos_encontrados:
        if produto_bloqueado(produto.nome):
            continue

        assinatura, base, medida_valor, medida_unidade = dados_assinatura_do_produto(produto)

        if not assinatura or not base:
            continue

        base_norm = normalizar(base).strip()

        # matching semântico exato por base
        if base_norm != q_norm:
            continue

        precos_raw = (
            db.query(PrecoProduto, UnidadeMercado, RedeMercado, Cidade)
            .join(UnidadeMercado, PrecoProduto.unidade_id == UnidadeMercado.id)
            .join(RedeMercado, UnidadeMercado.rede_id == RedeMercado.id)
            .join(Cidade, UnidadeMercado.cidade_id == Cidade.id)
            .filter(PrecoProduto.produto_id == produto.id)
            .all()
        )

        precos_validos = []
        for preco, unidade, rede, cidade in precos_raw:
            valor = float(preco.preco)
            if valor <= 0:
                continue

            precos_validos.append({
                "preco_id": preco.id,
                "preco": valor,
                "unidade_id": unidade.id,
                "unidade_nome": unidade.nome,
                "rede": rede.nome,
                "cidade": cidade.nome
            })

        if not precos_validos:
            continue

        precos_validos = sorted(precos_validos, key=lambda x: x["preco"])
        melhor_oferta_produto = precos_validos[0]

        if assinatura not in grupos:
            grupos[assinatura] = {
                "assinatura": assinatura,
                "base": base,
                "medida_valor": medida_valor,
                "medida_unidade": medida_unidade,
                "categoria": categoria_obj.nome if categoria_obj else None,
                "produtos": [],
                "menor_preco": None,
                "melhor_oferta": None,
                "total_ofertas": 0
            }

        grupos[assinatura]["produtos"].append({
            "produto_id": produto.id,
            "nome": produto.nome,
            "precos": precos_validos
        })

        grupos[assinatura]["total_ofertas"] += len(precos_validos)

        menor_atual = grupos[assinatura]["menor_preco"]
        if menor_atual is None or melhor_oferta_produto["preco"] < menor_atual:
            grupos[assinatura]["menor_preco"] = melhor_oferta_produto["preco"]
            grupos[assinatura]["melhor_oferta"] = melhor_oferta_produto

    grupos_ordenados = sorted(
        grupos.values(),
        key=lambda g: (
            g["menor_preco"] if g["menor_preco"] is not None else 999999,
            g["assinatura"]
        )
    )

    return {
        "q": q,
        "tokens_q": tokens_q,
        "total_grupos": len(grupos_ordenados),
        "grupos": grupos_ordenados[:limit_produtos]
    }
'''

content = content[:start] + novo_bloco

path.write_text(content, encoding="utf-8", newline="\n")
print("REWRITE_COMPARAR_PRODUTOS_OK")
