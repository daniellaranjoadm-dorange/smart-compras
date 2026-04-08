import sys
import io
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from app.db.base import SessionLocal
from app.models.entities import HistoricoPreco, Produto, UnidadeMercado

def to_decimal(v):
    return Decimal(str(v)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def main():
    db = SessionLocal()

    try:
        historicos = (
            db.query(HistoricoPreco)
            .order_by(
                HistoricoPreco.produto_id.asc(),
                HistoricoPreco.unidade_id.asc(),
                HistoricoPreco.id.asc()
            )
            .all()
        )

        grupos = defaultdict(list)
        for h in historicos:
            grupos[(h.produto_id, h.unidade_id)].append(h)

        mudancas = []

        for (produto_id, unidade_id), itens in grupos.items():
            if len(itens) < 2:
                continue

            anterior = itens[-2]
            atual = itens[-1]

            preco_anterior = to_decimal(anterior.preco)
            preco_atual = to_decimal(atual.preco)

            if preco_anterior == preco_atual:
                continue

            diferenca = (preco_atual - preco_anterior).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            variacao_percentual = ((preco_atual - preco_anterior) / preco_anterior) * Decimal("100")
            variacao_percentual = variacao_percentual.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            produto = db.query(Produto).filter(Produto.id == produto_id).first()
            unidade = db.query(UnidadeMercado).filter(UnidadeMercado.id == unidade_id).first()

            mudancas.append({
                "produto_id": produto_id,
                "produto_nome": produto.nome if produto else f"Produto {produto_id}",
                "assinatura": getattr(produto, "assinatura", None) if produto else None,
                "unidade_id": unidade_id,
                "unidade_nome": unidade.nome if unidade else f"Unidade {unidade_id}",
                "preco_anterior": preco_anterior,
                "preco_atual": preco_atual,
                "diferenca": diferenca,
                "variacao_percentual": variacao_percentual,
                "tipo": "queda" if preco_atual < preco_anterior else "alta",
            })

        mudancas.sort(key=lambda x: abs(x["variacao_percentual"]), reverse=True)

        print("===== MUDANCAS DE PRECO =====")
        print(f"total: {len(mudancas)}")
        print("")

        for m in mudancas[:100]:
            print(
                f"tipo={m['tipo']} | "
                f"produto_id={m['produto_id']} | "
                f"produto={m['produto_nome']} | "
                f"assinatura={m['assinatura']} | "
                f"unidade={m['unidade_nome']} | "
                f"anterior={m['preco_anterior']} | "
                f"atual={m['preco_atual']} | "
                f"diferenca={m['diferenca']} | "
                f"variacao={m['variacao_percentual']}%"
            )

    finally:
        db.close()

if __name__ == "__main__":
    main()
