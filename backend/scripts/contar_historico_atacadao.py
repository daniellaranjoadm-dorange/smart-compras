import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from app.db.base import SessionLocal
from app.models.entities import HistoricoPreco, UnidadeMercado

db = SessionLocal()

try:
    unidade = db.query(UnidadeMercado).filter_by(nome="Atacadao Rio Grande").first()

    total_geral = db.query(HistoricoPreco).count()
    print(f"ANTES_total_historico={total_geral}")

    if unidade:
        total_unidade = db.query(HistoricoPreco).filter(
            HistoricoPreco.unidade_id == unidade.id
        ).count()
        print(f"ANTES_total_historico_atacadao={total_unidade}")
    else:
        print("ANTES_unidade_nao_encontrada")

finally:
    db.close()
