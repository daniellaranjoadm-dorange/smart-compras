import unicodedata

from app.db.base import SessionLocal
from app.models.entities import Produto

CATEGORIAS = {
    "alimento": [
        "arroz", "feijao", "acucar", "oleo", "sal", "leite", "farinha"
    ],
    "automotivo": [
        "lubrificante", "motor", "diesel", "ipiranga", "castrol"
    ],
    "higiene": [
        "corporal", "cabelo", "condicionante", "serum", "cosmetico"
    ],
    "casa": [
        "peroba", "desengripante", "limpeza"
    ]
}


def normalizar(texto):
    texto = texto.lower()
    texto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in texto if not unicodedata.combining(c))


def classificar(nome):
    nome = normalizar(nome)

    for categoria, termos in CATEGORIAS.items():
        for termo in termos:
            if termo in nome:
                return categoria

    return "outros"


def run():
    db = SessionLocal()

    produtos = db.query(Produto).all()

    contagem = {}

    for p in produtos:
        cat = classificar(p.nome)

        if cat not in contagem:
            contagem[cat] = 0

        contagem[cat] += 1

    print()
    print("===== DISTRIBUICAO POR CATEGORIA =====")

    for cat, qtd in contagem.items():
        print(f"{cat}: {qtd}")

    print()

    print("===== EXEMPLOS DE NAO-ALIMENTO =====")

    for p in produtos:
        cat = classificar(p.nome)
        if cat != "alimento":
            print(f"[{cat}] {p.nome}")

    db.close()


if __name__ == "__main__":
    run()
