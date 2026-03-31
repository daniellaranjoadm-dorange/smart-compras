from sqlalchemy.orm import Session

from app.models.entities import ItemListaCompra, ListaCompra, PrecoProduto, Produto, RedeMercado, UnidadeMercado


def comparar_lista_por_cidade(db: Session, lista_id: int, cidade_id: int) -> dict:
    lista = db.query(ListaCompra).filter(ListaCompra.id == lista_id).first()
    if not lista:
        return {
            "lista_id": lista_id,
            "lista_nome": "",
            "cidade_id": cidade_id,
            "melhor_unidade_id": None,
            "melhor_unidade_nome": None,
            "melhor_rede_nome": None,
            "melhor_total": None,
            "unidades": [],
        }

    itens_lista = (
        db.query(ItemListaCompra, Produto)
        .join(Produto, Produto.id == ItemListaCompra.produto_id)
        .filter(ItemListaCompra.lista_id == lista_id)
        .all()
    )

    unidades = (
        db.query(UnidadeMercado, RedeMercado)
        .join(RedeMercado, RedeMercado.id == UnidadeMercado.rede_id)
        .filter(UnidadeMercado.cidade_id == cidade_id)
        .order_by(UnidadeMercado.nome)
        .all()
    )

    resultado_unidades = []

    for unidade, rede in unidades:
        total = 0.0
        itens_encontrados = 0
        itens_faltantes = 0
        itens_resultado = []

        for item, produto in itens_lista:
            preco_obj = (
                db.query(PrecoProduto)
                .filter(
                    PrecoProduto.produto_id == produto.id,
                    PrecoProduto.unidade_id == unidade.id,
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

        if itens_encontrados > 0:
            resultado_unidades.append(
                {
                    "unidade_id": unidade.id,
                    "unidade_nome": unidade.nome,
                    "rede_nome": rede.nome,
                    "cidade_id": unidade.cidade_id,
                    "total": round(total, 2),
                    "itens_encontrados": itens_encontrados,
                    "itens_faltantes": itens_faltantes,
                    "completo": itens_faltantes == 0,
                    "itens": itens_resultado,
                }
            )

    unidades_completas = [u for u in resultado_unidades if u["completo"]]
    melhor = min(unidades_completas, key=lambda x: x["total"]) if unidades_completas else None

    return {
        "lista_id": lista.id,
        "lista_nome": lista.nome,
        "cidade_id": cidade_id,
        "melhor_unidade_id": melhor["unidade_id"] if melhor else None,
        "melhor_unidade_nome": melhor["unidade_nome"] if melhor else None,
        "melhor_rede_nome": melhor["rede_nome"] if melhor else None,
        "melhor_total": melhor["total"] if melhor else None,
        "unidades": resultado_unidades,
    }


def comparar_lista_otimizada_por_cidade(db: Session, lista_id: int, cidade_id: int) -> dict:
    comparacao = comparar_lista_por_cidade(db, lista_id, cidade_id)

    if not comparacao["lista_nome"]:
        return {
            "lista_id": lista_id,
            "lista_nome": "",
            "cidade_id": cidade_id,
            "total_otimizado": 0.0,
            "melhor_unidade_id": None,
            "melhor_unidade_nome": None,
            "melhor_rede_nome": None,
            "melhor_total": None,
            "economia_vs_melhor_unidade": None,
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

    unidades_da_cidade = (
        db.query(UnidadeMercado, RedeMercado)
        .join(RedeMercado, RedeMercado.id == UnidadeMercado.rede_id)
        .filter(UnidadeMercado.cidade_id == cidade_id)
        .all()
    )

    itens_otimizados = []
    total_otimizado = 0.0
    itens_encontrados = 0
    itens_faltantes = 0

    for item, produto in itens_lista:
        opcoes = []

        for unidade, rede in unidades_da_cidade:
            preco_obj = (
                db.query(PrecoProduto)
                .filter(
                    PrecoProduto.produto_id == produto.id,
                    PrecoProduto.unidade_id == unidade.id,
                )
                .first()
            )

            if preco_obj:
                opcoes.append((preco_obj, unidade, rede))

        if not opcoes:
            itens_faltantes += 1
            itens_otimizados.append(
                {
                    "produto_id": produto.id,
                    "produto_nome": produto.nome,
                    "quantidade": item.quantidade,
                    "unidade_id": None,
                    "unidade_nome": None,
                    "rede_nome": None,
                    "preco_unitario": None,
                    "subtotal": None,
                    "disponivel": False,
                }
            )
            continue

        melhor_preco_obj, melhor_unidade, melhor_rede = min(opcoes, key=lambda x: float(x[0].preco))
        preco_unitario = float(melhor_preco_obj.preco)
        subtotal = round(preco_unitario * item.quantidade, 2)

        total_otimizado += subtotal
        itens_encontrados += 1

        itens_otimizados.append(
            {
                "produto_id": produto.id,
                "produto_nome": produto.nome,
                "quantidade": item.quantidade,
                "unidade_id": melhor_unidade.id,
                "unidade_nome": melhor_unidade.nome,
                "rede_nome": melhor_rede.nome,
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
        "cidade_id": cidade_id,
        "total_otimizado": round(total_otimizado, 2),
        "melhor_unidade_id": comparacao["melhor_unidade_id"],
        "melhor_unidade_nome": comparacao["melhor_unidade_nome"],
        "melhor_rede_nome": comparacao["melhor_rede_nome"],
        "melhor_total": comparacao["melhor_total"],
        "economia_vs_melhor_unidade": economia,
        "itens_encontrados": itens_encontrados,
        "itens_faltantes": itens_faltantes,
        "completo": itens_faltantes == 0,
        "itens": itens_otimizados,
    }


def gerar_resumo_inteligente_compra(db: Session, lista_id: int, cidade_id: int) -> dict:
    comparacao = comparar_lista_por_cidade(db, lista_id, cidade_id)
    otimizada = comparar_lista_otimizada_por_cidade(db, lista_id, cidade_id)

    if not comparacao["lista_nome"]:
        return {}

    total_melhor_unidade = comparacao["melhor_total"]
    total_otimizado = otimizada["total_otimizado"]
    economia_valor = otimizada["economia_vs_melhor_unidade"]

    economia_percentual = None
    if total_melhor_unidade and total_melhor_unidade > 0 and economia_valor is not None:
        economia_percentual = round((economia_valor / total_melhor_unidade) * 100, 2)

    unidades_usadas = {
        item["unidade_id"]
        for item in otimizada["itens"]
        if item["unidade_id"] is not None
    }

    quantidade_mercados_otimizados = len(unidades_usadas)

    vale_dividir = False
    if economia_valor is not None:
        vale_dividir = economia_valor >= 2.0 or quantidade_mercados_otimizados <= 1

    if quantidade_mercados_otimizados <= 1:
        recomendacao = (
            f"Comprar tudo em {comparacao['melhor_unidade_nome']} e a melhor opcao, "
            f"porque a compra otimizada nao exige dividir entre mercados."
        )
    elif economia_valor is not None and economia_valor >= 2.0:
        recomendacao = (
            f"Vale dividir a compra. A economia estimada e de R$ {economia_valor:.2f} "
            f"em relacao a comprar tudo em {comparacao['melhor_unidade_nome']}."
        )
    else:
        recomendacao = (
            f"A diferenca e pequena. Comprar tudo em {comparacao['melhor_unidade_nome']} "
            f"pode valer mais pela praticidade do que dividir a compra."
        )

    return {
        "lista_id": comparacao["lista_id"],
        "lista_nome": comparacao["lista_nome"],
        "cidade_id": cidade_id,
        "melhor_unidade_id": comparacao["melhor_unidade_id"],
        "melhor_unidade_nome": comparacao["melhor_unidade_nome"],
        "melhor_rede_nome": comparacao["melhor_rede_nome"],
        "total_melhor_unidade": total_melhor_unidade,
        "total_otimizado": total_otimizado,
        "economia_valor": economia_valor,
        "economia_percentual": economia_percentual,
        "quantidade_mercados_otimizados": quantidade_mercados_otimizados,
        "vale_dividir_compra": vale_dividir,
        "recomendacao": recomendacao,
    }
