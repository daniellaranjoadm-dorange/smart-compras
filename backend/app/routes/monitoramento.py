from decimal import Decimal, ROUND_HALF_UP
from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.base import SessionLocal
from app.models.entities import HistoricoPreco, Produto, UnidadeMercado

router = APIRouter(prefix="/api/monitoramento", tags=["monitoramento"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def to_decimal(v):
    return Decimal(str(v)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

@router.get("/mudancas-preco")
def listar_mudancas_preco(db: Session = Depends(get_db)):
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
            "unidade_id": unidade_id,
            "unidade": unidade.nome if unidade else f"Unidade {unidade_id}",
            "preco_anterior": float(preco_anterior),
            "preco_atual": float(preco_atual),
            "diferenca": float(diferenca),
            "variacao_percentual": float(variacao_percentual),
        })

    mudancas.sort(key=lambda x: abs(x["variacao_percentual"]), reverse=True)

    return {
        "total": len(mudancas),
        "itens": mudancas
    }
