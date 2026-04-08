import sys
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy import func

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from app.db.base import SessionLocal
from app.models.entities import Produto, PrecoProduto, HistoricoPreco, UnidadeMercado

def main():
    db = SessionLocal()

    try:
        unidade = db.query(UnidadeMercado).filter_by(nome="Atacadao Rio Grande").first()
        if not unidade:
            print("ERRO: unidade não encontrada")
            return

        alvo = (
            db.query(
                HistoricoPreco.produto_id,
                HistoricoPreco.unidade_id,
                func.count(HistoricoPreco.id).label("qtd")
            )
            .join(Produto, Produto.id == HistoricoPreco.produto_id)
            .filter(HistoricoPreco.unidade_id == unidade.id)
            .filter(Produto.assinatura != None)
            .group_by(HistoricoPreco.produto_id, HistoricoPreco.unidade_id)
            .having(func.count(HistoricoPreco.id) >= 1)
            .order_by(func.count(HistoricoPreco.id).desc(), HistoricoPreco.produto_id.asc())
            .first()
        )

        if not alvo:
            print("ERRO: nenhum produto com histórico anterior encontrado para o Atacadao")
            return

        produto_id = alvo.produto_id
        unidade_id = alvo.unidade_id

        produto = db.query(Produto).filter(Produto.id == produto_id).first()
        preco_row = db.query(PrecoProduto).filter_by(produto_id=produto_id, unidade_id=unidade_id).first()

        if not produto:
            print("ERRO: produto não encontrado")
            return

        if not preco_row:
            print("ERRO: PrecoProduto não encontrado")
            return

        preco_original = Decimal(str(preco_row.preco)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        novo_preco = (preco_original * Decimal("0.80")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        print("===== SIMULACAO COM HISTORICO =====")
        print(f"produto_id: {produto.id}")
        print(f"produto: {produto.nome}")
        print(f"assinatura: {produto.assinatura}")
        print(f"unidade: {unidade.nome}")
        print(f"historicos_anteriores: {alvo.qtd}")
        print(f"preco_original: {preco_original}")
        print(f"novo_preco: {novo_preco}")

        preco_row.preco = novo_preco

        db.add(HistoricoPreco(
            produto_id=produto.id,
            unidade_id=unidade.id,
            preco=novo_preco
        ))

        db.commit()

        print("")
        print("Simulação aplicada com sucesso")

    finally:
        db.close()

if __name__ == "__main__":
    main()
