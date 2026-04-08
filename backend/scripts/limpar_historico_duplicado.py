import sys
from pathlib import Path
from collections import defaultdict
from decimal import Decimal

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from app.db.base import SessionLocal
from app.models.entities import HistoricoPreco

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

        ids_para_remover = []
        total_grupos = 0
        total_removidos = 0

        for chave, itens in grupos.items():
            total_grupos += 1
            ultimo_preco = None
            primeiro = True

            for h in itens:
                preco_atual = Decimal(str(h.preco))

                if primeiro:
                    ultimo_preco = preco_atual
                    primeiro = False
                    continue

                if preco_atual == ultimo_preco:
                    ids_para_remover.append(h.id)
                    total_removidos += 1
                else:
                    ultimo_preco = preco_atual

        print("===== ANALISE LIMPEZA HISTORICO =====")
        print(f"grupos: {total_grupos}")
        print(f"registros_duplicados_consecutivos: {total_removidos}")

        if ids_para_remover:
            print("")
            print("===== AMOSTRA IDS REMOVER =====")
            for i in ids_para_remover[:30]:
                print(i)

        if ids_para_remover:
            (
                db.query(HistoricoPreco)
                .filter(HistoricoPreco.id.in_(ids_para_remover))
                .delete(synchronize_session=False)
            )
            db.commit()

        total_final = db.query(HistoricoPreco).count()

        print("")
        print("===== LIMPEZA FINALIZADA =====")
        print(f"removidos: {total_removidos}")
        print(f"total_historico_restante: {total_final}")

    finally:
        db.close()

if __name__ == "__main__":
    main()
