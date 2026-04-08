import unicodedata

from app.db.base import SessionLocal
from app.models.entities import Produto, Categoria

CATEGORIAS = {
    "mercearia": [
        "arroz", "feijao", "acucar", "oleo", "sal", "farinha", "leite", "cafe",
        "macarrao", "biscoito", "bolacha", "chocolate", "bombom", "wafer",
        "torrada", "bolo", "molho", "extrato", "milho", "ervilha",
        "atum", "sardinha", "azeite", "vinagre", "granola", "aveia",
        "farofa", "margarina", "pasta de amendoim", "creme de leite",
        "adocante", "gelatina", "ketchup", "mostarda", "paçoca", "pacoca",
        "mucilon", "cereal", "barra de cereais", "composto lacteo"
    ],
    "bebida": [
        "cerveja", "refrigerante", "suco", "agua", "energetico",
        "cha", "tonica", "guarana", "isotonico", "bebida vegetal",
        "bebida lactea", "powerade", "cereser"
    ],
    "perecivel": [
        "carne", "frango", "peixe", "linguica", "salsicha",
        "presunto", "queijo", "manteiga", "iogurte",
        "congelado", "pizza", "batata", "acai", "sobremesa lactea",
        "requeijao"
    ],
    "limpeza": [
        "detergente", "sabao", "amaciante", "desinfetante",
        "lava roupas", "lava-roupas", "lava roupa", "multiuso", "cloro",
        "papel higienico", "lava louca", "desengordurante", "limpador"
    ],
    "higiene": [
        "shampoo", "condicionador", "sabonete", "creme",
        "desodorante", "fralda", "hidratante", "absorvente"
    ],
    "infantil": [
        "formula infantil", "aptamil", "ninho fases", "aptanutri"
    ],
    "casa": [
        "copo", "prato", "talher", "pote", "garrafa",
        "escorredor", "fritadeira", "air fryer", "forma"
    ]
}


def normalizar(texto):
    texto = (texto or "").lower().strip()
    texto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in texto if not unicodedata.combining(c))


def classificar(nome):
    nome = normalizar(nome)

    for categoria, termos in CATEGORIAS.items():
        for termo in termos:
            if termo in nome:
                return categoria

    return "outros"


def get_or_create_categoria(db, nome):
    cat = db.query(Categoria).filter_by(nome=nome).first()
    if not cat:
        cat = Categoria(nome=nome)
        db.add(cat)
        db.commit()
        db.refresh(cat)
    return cat


def run():
    db = SessionLocal()

    mapa_categorias = {}
    for nome_categoria in list(CATEGORIAS.keys()) + ["outros"]:
        cat = get_or_create_categoria(db, nome_categoria)
        mapa_categorias[nome_categoria] = cat

    produtos = db.query(Produto).all()

    contagem = {}
    atualizados = 0

    for produto in produtos:
        nome_categoria = classificar(produto.nome)
        categoria = mapa_categorias[nome_categoria]

        if produto.categoria_id != categoria.id:
            produto.categoria_id = categoria.id
            atualizados += 1

        contagem[nome_categoria] = contagem.get(nome_categoria, 0) + 1

    db.commit()

    print()
    print("===== CATEGORIAS SALVAS NO BANCO =====")
    for nome in sorted(contagem.keys()):
        print(f"{nome}: {contagem[nome]}")

    print()
    print(f"TOTAL PRODUTOS ATUALIZADOS: {atualizados}")

    db.close()


if __name__ == "__main__":
    run()
