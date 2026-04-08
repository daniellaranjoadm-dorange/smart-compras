import unicodedata

from app.db.base import SessionLocal
from app.models.entities import Produto

CATEGORIAS = {
    "mercearia": [
        "arroz", "feijao", "acucar", "oleo", "sal", "farinha", "leite", "cafe",
        "macarrao", "biscoito", "bolacha", "chocolate", "bombom", "wafer",
        "torrada", "bolo", "molho", "extrato", "milho", "ervilha",
        "atum", "sardinha", "azeite", "vinagre", "granola", "aveia",
        "farofa", "margarina", "pasta de amendoim", "creme de leite"
    ],
    "bebida": [
        "cerveja", "refrigerante", "suco", "agua", "energetico",
        "cha", "tonica", "guarana", "isotonico"
    ],
    "perecivel": [
        "carne", "frango", "peixe", "linguica", "salsicha",
        "presunto", "queijo", "manteiga", "iogurte",
        "congelado", "pizza", "batata", "acai"
    ],
    "limpeza": [
        "detergente", "sabao", "amaciante", "desinfetante",
        "lava roupas", "lava-roupas", "multiuso", "cloro"
    ],
    "higiene": [
        "shampoo", "condicionador", "sabonete", "creme",
        "desodorante", "fralda", "hidratante"
    ],
    "infantil": [
        "formula infantil", "aptamil", "ninho fases", "aptanutri"
    ],
    "casa": [
        "copo", "prato", "talher", "pote", "garrafa"
    ]
}


def normalizar(texto):
    texto = texto.lower().strip()
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
    exemplos_outros = []

    for p in produtos:
        cat = classificar(p.nome)
        contagem[cat] = contagem.get(cat, 0) + 1

        if cat == "outros" and len(exemplos_outros) < 100:
            exemplos_outros.append(p.nome)

    print()
    print("===== DISTRIBUICAO V4 =====")
    for cat in sorted(contagem.keys()):
        print(f"{cat}: {contagem[cat]}")

    print()
    print("===== OUTROS (AMOSTRA) =====")
    for nome in exemplos_outros:
        print(nome)

    db.close()


if __name__ == "__main__":
    run()
