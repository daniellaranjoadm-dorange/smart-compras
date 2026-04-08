import unicodedata

from app.db.base import SessionLocal
from app.models.entities import Produto

CATEGORIAS = {
    "mercearia": [
        "arroz", "feijao", "acucar", "oleo", "sal", "farinha"
    ],
    "bebida": [
        "cerveja", "refrigerante", "suco", "agua", "energetico"
    ],
    "higiene": [
        "shampoo", "condicionador", "sabonete", "creme", "serum"
    ],
    "limpeza": [
        "detergente", "sabao", "amaciante", "desinfetante"
    ],
    "automotivo": [
        "lubrificante", "motor", "diesel", "oleo lub"
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
    print("===== DISTRIBUICAO REAL =====")

    for cat, qtd in contagem.items():
        print(f"{cat}: {qtd}")

    print()
    print("===== EXEMPLOS DE OUTROS =====")

    for p in produtos[:200]:
        cat = classificar(p.nome)
        if cat == "outros":
            print(p.nome)

    db.close()


if __name__ == "__main__":
    run()
