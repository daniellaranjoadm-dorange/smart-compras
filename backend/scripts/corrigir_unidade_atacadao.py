from app.db.base import SessionLocal
from app.models.entities import UnidadeMercado, PrecoProduto, HistoricoPreco

UNIDADE_ORIGEM = 8
UNIDADE_DESTINO = 9


def run():
    db = SessionLocal()

    origem = db.query(UnidadeMercado).filter(UnidadeMercado.id == UNIDADE_ORIGEM).first()
    destino = db.query(UnidadeMercado).filter(UnidadeMercado.id == UNIDADE_DESTINO).first()

    if not origem:
        raise Exception(f"Unidade de origem nao encontrada: {UNIDADE_ORIGEM}")

    if not destino:
        raise Exception(f"Unidade de destino nao encontrada: {UNIDADE_DESTINO}")

    print()
    print("===== INICIO DA CORRECAO =====")
    print(f"ORIGEM : {origem.id} | {origem.nome}")
    print(f"DESTINO: {destino.id} | {destino.nome}")
    print()

    precos_origem = db.query(PrecoProduto).filter(PrecoProduto.unidade_id == UNIDADE_ORIGEM).all()

    movidos = 0
    removidos_por_duplicidade = 0

    for preco_origem in precos_origem:
        preco_destino = (
            db.query(PrecoProduto)
            .filter(
                PrecoProduto.unidade_id == UNIDADE_DESTINO,
                PrecoProduto.produto_id == preco_origem.produto_id
            )
            .first()
        )

        if preco_destino:
            db.delete(preco_origem)
            removidos_por_duplicidade += 1
        else:
            preco_origem.unidade_id = UNIDADE_DESTINO
            movidos += 1

    db.commit()

    historicos_origem = db.query(HistoricoPreco).filter(HistoricoPreco.unidade_id == UNIDADE_ORIGEM).all()

    historicos_movidos = 0
    for historico in historicos_origem:
        historico.unidade_id = UNIDADE_DESTINO
        historicos_movidos += 1

    db.commit()

    origem.nome = f"LEGADO_NAO_USAR_{origem.nome}"
    db.commit()

    total_origem = db.query(PrecoProduto).filter(PrecoProduto.unidade_id == UNIDADE_ORIGEM).count()
    total_destino = db.query(PrecoProduto).filter(PrecoProduto.unidade_id == UNIDADE_DESTINO).count()

    print("===== RESUMO =====")
    print(f"PRECOS MOVIDOS: {movidos}")
    print(f"PRECOS REMOVIDOS POR DUPLICIDADE: {removidos_por_duplicidade}")
    print(f"HISTORICOS MOVIDOS: {historicos_movidos}")
    print(f"TOTAL PREÇOS NA ORIGEM APOS CORRECAO: {total_origem}")
    print(f"TOTAL PREÇOS NO DESTINO APOS CORRECAO: {total_destino}")
    print(f"NOME NOVO UNIDADE ORIGEM: {origem.nome}")

    db.close()


if __name__ == "__main__":
    run()
