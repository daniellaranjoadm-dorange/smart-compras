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

QUEDA_MINIMA_PERCENTUAL = Decimal("3")
MIN_REGISTROS_ANTERIORES = 2

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

        promocoes = []
        total_grupos = 0
        total_com_historico_suficiente = 0

        for (produto_id, unidade_id), itens in grupos.items():
            total_grupos += 1

            if len(itens) < (MIN_REGISTROS_ANTERIORES + 1):
                continue

            total_com_historico_suficiente += 1

            atual = itens[-1]
            anteriores = itens[:-1][-MIN_REGISTROS_ANTERIORES:]

            preco_atual = to_decimal(atual.preco)
            precos_anteriores = [to_decimal(x.preco) for x in anteriores]

            media_anterior = sum(precos_anteriores) / Decimal(len(precos_anteriores))
            media_anterior = media_anterior.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            if media_anterior <= 0:
                continue

            queda_percentual = ((media_anterior - preco_atual) / media_anterior) * Decimal("100")
            queda_percentual = queda_percentual.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            produto = db.query(Produto).filter(Produto.id == produto_id).first()
            unidade = db.query(UnidadeMercado).filter(UnidadeMercado.id == unidade_id).first()

            nome_produto = produto.nome if produto else f"Produto {produto_id}"
            assinatura = getattr(produto, "assinatura", None) if produto else None
            nome_unidade = unidade.nome if unidade else f"Unidade {unidade_id}"

            print(
                f"[DEBUG] produto_id={produto_id} | "
                f"produto={nome_produto} | "
                f"assinatura={assinatura} | "
                f"unidade={nome_unidade} | "
                f"preco_atual={preco_atual} | "
                f"media_anterior={media_anterior} | "
                f"queda={queda_percentual}% | "
                f"registros={len(itens)}"
            )

            if queda_percentual < QUEDA_MINIMA_PERCENTUAL:
                continue

            promocoes.append({
                "produto_id": produto_id,
                "produto_nome": nome_produto,
                "assinatura": assinatura,
                "unidade_id": unidade_id,
                "unidade_nome": nome_unidade,
                "preco_atual": preco_atual,
                "media_anterior": media_anterior,
                "queda_percentual": queda_percentual,
                "registros": len(itens),
            })

        promocoes.sort(key=lambda x: x["queda_percentual"], reverse=True)

        print("")
        print("===== RESUMO DEBUG =====")
        print(f"grupos_total: {total_grupos}")
        print(f"grupos_com_historico_suficiente: {total_com_historico_suficiente}")

        print("")
        print("===== PROMOCOES DETECTADAS =====")
        print(f"total: {len(promocoes)}")
        print("")

        for p in promocoes[:100]:
            print(
                f"produto_id={p['produto_id']} | "
                f"produto={p['produto_nome']} | "
                f"assinatura={p['assinatura']} | "
                f"unidade={p['unidade_nome']} | "
                f"preco_atual={p['preco_atual']} | "
                f"media_anterior={p['media_anterior']} | "
                f"queda={p['queda_percentual']}% | "
                f"registros={p['registros']}"
            )

    finally:
        db.close()

if __name__ == "__main__":
    main()
