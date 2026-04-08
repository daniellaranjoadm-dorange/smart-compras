from app.db.base import SessionLocal
from app.models.entities import UnidadeMercado, RedeMercado, Cidade, PrecoProduto

def run():
    db = SessionLocal()

    unidades = (
        db.query(UnidadeMercado, RedeMercado, Cidade)
        .join(RedeMercado, UnidadeMercado.rede_id == RedeMercado.id)
        .join(Cidade, UnidadeMercado.cidade_id == Cidade.id)
        .order_by(UnidadeMercado.id.asc())
        .all()
    )

    print()
    print("===== AUDITORIA DE UNIDADES =====")
    print()

    for unidade, rede, cidade in unidades:
        total_precos = db.query(PrecoProduto).filter(PrecoProduto.unidade_id == unidade.id).count()

        print(f"UNIDADE_ID: {unidade.id}")
        print(f"NOME: {unidade.nome}")
        print(f"REDE: {rede.nome}")
        print(f"CIDADE: {cidade.nome}")
        print(f"TOTAL_PRECOS: {total_precos}")
        print("-" * 80)

    db.close()

if __name__ == "__main__":
    run()
