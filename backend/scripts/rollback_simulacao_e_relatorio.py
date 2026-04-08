import sys
import io
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
from collections import defaultdict
import csv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from app.db.base import SessionLocal
from app.models.entities import HistoricoPreco, Produto, UnidadeMercado, PrecoProduto

def to_decimal(v):
    return Decimal(str(v)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def rollback_simulacao(db):
    produto = db.query(Produto).filter(Produto.id == 15).first()
    unidade = db.query(UnidadeMercado).filter_by(nome="Atacadao Rio Grande").first()

    if not produto or not unidade:
        print("ROLLBACK: produto ou unidade não encontrados")
        return

    preco_row = db.query(PrecoProduto).filter_by(produto_id=produto.id, unidade_id=unidade.id).first()
    if not preco_row:
        print("ROLLBACK: PrecoProduto não encontrado")
        return

    preco_original = Decimal("14.90")
    preco_atual = to_decimal(preco_row.preco)

    if preco_atual == preco_original:
        print("ROLLBACK: preço já está restaurado")
        return

    preco_row.preco = preco_original
    db.add(HistoricoPreco(
        produto_id=produto.id,
        unidade_id=unidade.id,
        preco=preco_original
    ))
    db.commit()

    print("===== ROLLBACK SIMULACAO =====")
    print(f"produto: {produto.nome}")
    print(f"preco_restaurado: {preco_original}")

def gerar_relatorio_mudancas(db):
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
            "tipo": "queda" if preco_atual < preco_anterior else "alta",
            "produto_id": produto_id,
            "produto": produto.nome if produto else f"Produto {produto_id}",
            "assinatura": getattr(produto, "assinatura", None) if produto else None,
            "unidade": unidade.nome if unidade else f"Unidade {unidade_id}",
            "preco_anterior": str(preco_anterior),
            "preco_atual": str(preco_atual),
            "diferenca": str(diferenca),
            "variacao_percentual": str(variacao_percentual),
        })

    mudancas.sort(key=lambda x: abs(Decimal(x["variacao_percentual"])), reverse=True)

    output = BASE_DIR / "logs" / "mudancas_preco.csv"
    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "tipo",
                "produto_id",
                "produto",
                "assinatura",
                "unidade",
                "preco_anterior",
                "preco_atual",
                "diferenca",
                "variacao_percentual",
            ]
        )
        writer.writeheader()
        writer.writerows(mudancas)

    print("")
    print("===== RELATORIO DE MUDANCAS =====")
    print(f"total: {len(mudancas)}")
    print(f"arquivo: {output}")

    for m in mudancas[:20]:
        print(
            f"tipo={m['tipo']} | "
            f"produto={m['produto']} | "
            f"unidade={m['unidade']} | "
            f"anterior={m['preco_anterior']} | "
            f"atual={m['preco_atual']} | "
            f"variacao={m['variacao_percentual']}%"
        )

def main():
    db = SessionLocal()
    try:
        rollback_simulacao(db)
        gerar_relatorio_mudancas(db)
    finally:
        db.close()

if __name__ == "__main__":
    main()
