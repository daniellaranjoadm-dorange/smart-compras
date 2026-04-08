import unicodedata

from app.db.base import SessionLocal
from app.models.entities import Produto

CATEGORIAS = {
    "mercearia": [
        "arroz", "feijao", "acucar", "oleo", "sal", "farinha", "leite", "cafe",
        "macarrao", "biscoito", "bolacha", "chocolate", "bombom", "wafer",
        "torrada", "bolo", "pao de mel", "alga", "nori", "molho", "extrato",
        "milho", "ervilha", "atum", "sardinha", "azeite", "vinagre", "granola",
        "aveia", "cereal", "achocolatado", "doce", "geleia", "mel", "fermento"
    ],
    "bebida": [
        "cerveja", "refrigerante", "suco", "agua", "energetico", "cha", "cajuina",
        "tonica", "guarana", "cola", "uva", "laranja", "limao"
    ],
    "limpeza": [
        "detergente", "sabao", "amaciante", "desinfetante", "lava roupas",
        "lava-roupas", "multiuso", "alvejante", "agua sanitaria", "limpador",
        "limpeza", "cloro", "desengordurante"
    ],
    "higiene": [
        "shampoo", "condicionador", "sabonete", "creme", "serum", "desodorante",
        "escova dental", "pasta de dente", "absorvente", "fralda", "hidratante"
    ],
    "casa": [
        "copo", "prato", "talher", "pote", "garrafa", "caneca", "xicara",
        "assadeira", "forma", "travessa", "tigela", "utensilio"
    ],
    "perecivel": [
        "carne", "frango", "bovina", "suina", "peixe", "linguica", "salsicha",
        "presunto", "mussarela", "queijo", "manteiga", "iogurte", "congelado",
        "pao de queijo", "hamburguer", "empanado"
    ],
    "automotivo": [
        "lubrificante", "motor", "diesel", "oleo lub", "desengripante", "20w",
        "5w", "10w", "15w", "40 sl", "4t"
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

        if cat == "outros" and len(exemplos_outros) < 200:
            exemplos_outros.append(p.nome)

    print()
    print("===== DISTRIBUICAO REAL V3 =====")
    for cat in sorted(contagem.keys()):
        print(f"{cat}: {contagem[cat]}")

    print()
    print("===== EXEMPLOS DE OUTROS =====")
    for nome in exemplos_outros:
        print(nome)

    db.close()


if __name__ == "__main__":
    run()
