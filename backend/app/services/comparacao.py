from sqlalchemy.orm import Session

from app.models.entities import ItemListaCompra, ListaCompra, Mercado, PrecoProduto, Produto


def comparar_lista_por_mercado(db: Session, lista_id: int) -> dict:
    lista = db.query(ListaCompra).filter(ListaCompra.id == lista_id).first()
    if not lista:
        return {
            "lista_id": lista_id,
            "lista_nome": "",
            "melhor_mercado_id": None,
            "melhor_mercado_nome": None,
            "melhor_total": None,
            "mercados": [],
        }

    itens_lista = (
        db.query(ItemListaCompra, Produto)
        .join(Produto, Produto.id == ItemListaCompra.produto_id)
        .filter(ItemListaCompra.lista_id == lista_id)
        .all()
    )

    mercados = db.query(Mercado).order_by(Mercado.nome).all()
    resultado_mercados = []

    for mercado in mercados:
        total = 0.0
        itens_encontrados = 0
        itens_faltantes = 0
        itens_resultado = []

        for item, produto in itens_lista:
            preco_obj = (
                db.query(PrecoProduto)
                .filter(
                    PrecoProduto.produto_id == produto.id,
                    PrecoProduto.mercado_id == mercado.id,
                )
                .first()
            )

            if preco_obj:
                preco_unitario = float(preco_obj.preco)
                subtotal = round(preco_unitario * item.quantidade, 2)
                total += subtotal
                itens_encontrados += 1
                itens_resultado.append(
                    {
                        "produto_id": produto.id,
                        "produto_nome": produto.nome,
                        "quantidade": item.quantidade,
                        "preco_unitario": preco_unitario,
                        "subtotal": subtotal,
                        "disponivel": True,
                    }
                )
            else:
                itens_faltantes += 1
                itens_resultado.append(
                    {
                        "produto_id": produto.id,
                        "produto_nome": produto.nome,
                        "quantidade": item.quantidade,
                        "preco_unitario": None,
                        "subtotal": None,
                        "disponivel": False,
                    }
                )

        resultado_mercados.append(
            {
                "mercado_id": mercado.id,
                "mercado_nome": mercado.nome,
                "total": round(total, 2),
                "itens_encontrados": itens_encontrados,
                "itens_faltantes": itens_faltantes,
                "completo": itens_faltantes == 0,
                "itens": itens_resultado,
            }
        )

    mercados_completos = [m for m in resultado_mercados if m["completo"]]
    melhor = min(mercados_completos, key=lambda x: x["total"]) if mercados_completos else None

    return {
        "lista_id": lista.id,
        "lista_nome": lista.nome,
        "melhor_mercado_id": melhor["mercado_id"] if melhor else None,
        "melhor_mercado_nome": melhor["mercado_nome"] if melhor else None,
        "melhor_total": melhor["total"] if melhor else None,
        "mercados": resultado_mercados,
    }


def comparar_lista_otimizada(db: Session, lista_id: int) -> dict:
    comparacao = comparar_lista_por_mercado(db, lista_id)

    if not comparacao["lista_nome"]:
        return {
            "lista_id": lista_id,
            "lista_nome": "",
            "total_otimizado": 0.0,
            "melhor_mercado_unico_id": None,
            "melhor_mercado_unico_nome": None,
            "melhor_mercado_unico_total": None,
            "economia_vs_melhor_mercado": None,
            "itens_encontrados": 0,
            "itens_faltantes": 0,
            "completo": False,
            "itens": [],
        }

    lista = db.query(ListaCompra).filter(ListaCompra.id == lista_id).first()

    itens_lista = (
        db.query(ItemListaCompra, Produto)
        .join(Produto, Produto.id == ItemListaCompra.produto_id)
        .filter(ItemListaCompra.lista_id == lista_id)
        .all()
    )

    itens_otimizados = []
    total_otimizado = 0.0
    itens_encontrados = 0
    itens_faltantes = 0

    for item, produto in itens_lista:
        precos = (
            db.query(PrecoProduto, Mercado)
            .join(Mercado, Mercado.id == PrecoProduto.mercado_id)
            .filter(PrecoProduto.produto_id == produto.id)
            .all()
        )

        if not precos:
            itens_faltantes += 1
            itens_otimizados.append(
                {
                    "produto_id": produto.id,
                    "produto_nome": produto.nome,
                    "quantidade": item.quantidade,
                    "mercado_id": None,
                    "mercado_nome": None,
                    "preco_unitario": None,
                    "subtotal": None,
                    "disponivel": False,
                }
            )
            continue

        melhor_preco, melhor_mercado = min(precos, key=lambda x: float(x[0].preco))
        preco_unitario = float(melhor_preco.preco)
        subtotal = round(preco_unitario * item.quantidade, 2)

        total_otimizado += subtotal
        itens_encontrados += 1

        itens_otimizados.append(
            {
                "produto_id": produto.id,
                "produto_nome": produto.nome,
                "quantidade": item.quantidade,
                "mercado_id": melhor_mercado.id,
                "mercado_nome": melhor_mercado.nome,
                "preco_unitario": preco_unitario,
                "subtotal": subtotal,
                "disponivel": True,
            }
        )

    melhor_total = comparacao["melhor_total"]
    economia = None
    if melhor_total is not None:
        economia = round(melhor_total - round(total_otimizado, 2), 2)

    return {
        "lista_id": lista.id,
        "lista_nome": lista.nome,
        "total_otimizado": round(total_otimizado, 2),
        "melhor_mercado_unico_id": comparacao["melhor_mercado_id"],
        "melhor_mercado_unico_nome": comparacao["melhor_mercado_nome"],
        "melhor_mercado_unico_total": comparacao["melhor_total"],
        "economia_vs_melhor_mercado": economia,
        "itens_encontrados": itens_encontrados,
        "itens_faltantes": itens_faltantes,
        "completo": itens_faltantes == 0,
        "itens": itens_otimizados,
    }


def obter_melhor_preco_produto(db: Session, produto_id: int) -> dict:
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        return {}

    precos = (
        db.query(PrecoProduto, Mercado)
        .join(Mercado, Mercado.id == PrecoProduto.mercado_id)
        .filter(PrecoProduto.produto_id == produto_id)
        .all()
    )

    if not precos:
        return {
            "produto_id": produto.id,
            "produto_nome": produto.nome,
            "menor_preco": None,
            "mercado_menor_preco_id": None,
            "mercado_menor_preco_nome": None,
            "maior_preco": None,
            "mercado_maior_preco_id": None,
            "mercado_maior_preco_nome": None,
            "diferenca_absoluta": None,
            "variacao_percentual": None,
        }

    menor_preco_obj, mercado_menor = min(precos, key=lambda x: float(x[0].preco))
    maior_preco_obj, mercado_maior = max(precos, key=lambda x: float(x[0].preco))

    menor_preco = float(menor_preco_obj.preco)
    maior_preco = float(maior_preco_obj.preco)
    diferenca_absoluta = round(maior_preco - menor_preco, 2)

    variacao_percentual = None
    if menor_preco > 0:
        variacao_percentual = round((diferenca_absoluta / menor_preco) * 100, 2)

    return {
        "produto_id": produto.id,
        "produto_nome": produto.nome,
        "menor_preco": menor_preco,
        "mercado_menor_preco_id": mercado_menor.id,
        "mercado_menor_preco_nome": mercado_menor.nome,
        "maior_preco": maior_preco,
        "mercado_maior_preco_id": mercado_maior.id,
        "mercado_maior_preco_nome": mercado_maior.nome,
        "diferenca_absoluta": diferenca_absoluta,
        "variacao_percentual": variacao_percentual,
    }


def obter_melhores_precos_lista(db: Session, lista_id: int) -> list[dict]:
    itens_lista = (
        db.query(ItemListaCompra, Produto)
        .join(Produto, Produto.id == ItemListaCompra.produto_id)
        .filter(ItemListaCompra.lista_id == lista_id)
        .all()
    )

    resultado = []
    for _, produto in itens_lista:
        resultado.append(obter_melhor_preco_produto(db, produto.id))

    return resultado


def obter_dashboard_resumo_lista(db: Session, lista_id: int) -> dict:
    lista = db.query(ListaCompra).filter(ListaCompra.id == lista_id).first()
    if not lista:
        return {}

    itens_lista = (
        db.query(ItemListaCompra)
        .filter(ItemListaCompra.lista_id == lista_id)
        .all()
    )

    comparacao = comparar_lista_por_mercado(db, lista_id)
    otimizada = comparar_lista_otimizada(db, lista_id)
    melhores = obter_melhores_precos_lista(db, lista_id)

    item_maior_diferenca = None
    itens_com_diferenca = [i for i in melhores if i.get("diferenca_absoluta") is not None]
    if itens_com_diferenca:
        item_maior_diferenca = max(itens_com_diferenca, key=lambda x: x["diferenca_absoluta"])

    item_maior_variacao = None
    itens_com_variacao = [i for i in melhores if i.get("variacao_percentual") is not None]
    if itens_com_variacao:
        item_maior_variacao = max(itens_com_variacao, key=lambda x: x["variacao_percentual"])

    return {
        "lista_id": lista.id,
        "lista_nome": lista.nome,
        "quantidade_itens_lista": len(itens_lista),
        "itens_encontrados": otimizada["itens_encontrados"],
        "itens_faltantes": otimizada["itens_faltantes"],
        "melhor_mercado_unico_id": comparacao["melhor_mercado_id"],
        "melhor_mercado_unico_nome": comparacao["melhor_mercado_nome"],
        "melhor_mercado_unico_total": comparacao["melhor_total"],
        "total_otimizado": otimizada["total_otimizado"],
        "economia_total": otimizada["economia_vs_melhor_mercado"],
        "item_maior_diferenca": item_maior_diferenca,
        "item_maior_variacao": item_maior_variacao,
    }
