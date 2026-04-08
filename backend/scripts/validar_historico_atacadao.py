import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from app.db.base import SessionLocal
from app.models.entities import HistoricoPreco, UnidadeMercado

db = SessionLocal()

try:
    unidade = db.query(UnidadeMercado).filter_by(nome="Atacadao Rio Grande").first()

    total_historico = db.query(HistoricoPreco).count()

    print("===== VALIDACAO HISTORICO =====")
    print(f"unidade_encontrada: {bool(unidade)}")
    print(f"total_historico: {total_historico}")

    if unidade:
        total_unidade = db.query(HistoricoPreco).filter(
            HistoricoPreco.unidade_id == unidade.id
        ).count()
        print(f"total_historico_atacadao: {total_unidade}")

        ultimos = db.query(HistoricoPreco).filter(
            HistoricoPreco.unidade_id == unidade.id
        ).order_by(HistoricoPreco.id.desc()).limit(15).all()

        print("")
        print("===== ULTIMOS REGISTROS =====")
        for h in ultimos:
            print(
                f"id={h.id} | produto_id={h.produto_id} | unidade_id={h.unidade_id} | preco={h.preco}"
            )

finally:
    db.close()
