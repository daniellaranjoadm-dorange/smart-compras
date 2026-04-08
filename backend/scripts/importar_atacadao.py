import re
import requests
import unicodedata
from decimal import Decimal

from app.db.base import SessionLocal
from app.models.entities import (
    Produto,
    PrecoProduto,
    HistoricoPreco,
    UnidadeMercado,
    RedeMercado,
    Cidade,
    Estado,
    Categoria,
)

URL = "https://www.atacadao.com.br/api/io/_v/api/intelligent-search/product_search"

BUSCAS = [
    {
        "query": "arroz tipo 1",
        "aceitar": ["arroz"],
        "bloquear": [
            "mucilon", "biscoito", "vinagre", "macarrao", "pet", "cao", "caes",
            "swift", "perdigao", "congelado", "pronto", "brocolis", "palmito",
            "carreteiro", "cremoso", "porta escova", "coza", "chocolate"
        ],
        "peso_min_g": 500
    },
    {
        "query": "feijao carioca",
        "aceitar": ["feijao"],
        "bloquear": [
            "swift", "perdigao", "pet", "cao", "caes", "tempero", "pronto",
            "congelado", "caldo", "sopa", "feijoada"
        ],
        "peso_min_g": 500
    },
    {
        "query": "oleo soja",
        "aceitar": ["oleo"],
        "bloquear": ["essencial", "corporal", "capilar", "motor", "lubrificante", "desengripante"],
        "peso_min_g": 500
    },
    {
        "query": "acucar refinado",
        "aceitar": ["acucar"],
        "bloquear": ["mascavo", "diet", "adocante"],
        "peso_min_g": 500
    },
]

CATEGORIAS = {
    "mercearia": [
        "arroz", "feijao", "acucar", "oleo", "sal", "farinha", "leite", "cafe",
        "macarrao", "biscoito", "bolacha", "chocolate", "bombom", "wafer",
        "torrada", "bolo", "molho", "extrato", "milho", "ervilha",
        "atum", "sardinha", "azeite", "vinagre", "granola", "aveia",
        "farofa", "margarina", "pasta de amendoim", "creme de leite",
        "adocante", "gelatina", "ketchup", "mostarda", "pacoca",
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

CATEGORIAS_PERMITIDAS = {"mercearia", "bebida", "perecivel"}

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}


def normalizar(texto):
    if not texto:
        return ""
    texto = texto.lower().strip()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()


def extrair_medida(nome):
    nome_norm = normalizar(nome).replace(",", ".")

    padroes = [
        r"(\d+(?:\.\d+)?)\s*(kg)",
        r"(\d+(?:\.\d+)?)\s*(g)",
        r"(\d+(?:\.\d+)?)\s*(l)",
        r"(\d+(?:\.\d+)?)\s*(ml)",
    ]

    for padrao in padroes:
        m = re.search(padrao, nome_norm)
        if m:
            valor = float(m.group(1))
            unidade = m.group(2)

            if unidade == "kg":
                return valor * 1000, "g"
            if unidade == "l":
                return valor * 1000, "ml"
            return valor, unidade

    return None, None


def classificar(nome):
    nome = normalizar(nome)

    for categoria, termos in CATEGORIAS.items():
        for termo in termos:
            if termo in nome:
                return categoria

    return "outros"


def buscar_produtos(query, page):
    params = {
        "query": query,
        "page": page,
        "count": 20
    }

    resp = requests.get(URL, params=params, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data.get("products", [])


def relevante(nome, aceitar, bloquear, peso_min_g):
    nome_norm = normalizar(nome)

    if not any(a in nome_norm for a in aceitar):
        return False, "sem termo aceito"

    if any(b in nome_norm for b in bloquear):
        return False, "termo bloqueado"

    medida_valor, medida_unidade = extrair_medida(nome)
    if medida_valor is None:
        return False, "sem medida"

    if medida_unidade == "g" and medida_valor < peso_min_g:
        return False, "peso abaixo do minimo"

    if medida_unidade == "ml" and medida_valor < peso_min_g:
        return False, "volume abaixo do minimo"

    return True, "ok"


def get_contexto(db):
    estado = db.query(Estado).filter_by(uf="RS").first()
    if not estado:
        estado = Estado(nome="Rio Grande do Sul", uf="RS")
        db.add(estado)
        db.commit()
        db.refresh(estado)

    cidade = db.query(Cidade).filter_by(nome="Rio Grande", estado_id=estado.id).first()
    if not cidade:
        cidade = Cidade(nome="Rio Grande", estado_id=estado.id)
        db.add(cidade)
        db.commit()
        db.refresh(cidade)

    rede = db.query(RedeMercado).filter_by(nome="Atacadao").first()
    if not rede:
        rede = RedeMercado(nome="Atacadao")
        db.add(rede)
        db.commit()
        db.refresh(rede)

    unidade = db.query(UnidadeMercado).filter_by(
        nome="Atacadao Rio Grande",
        rede_id=rede.id,
        cidade_id=cidade.id
    ).first()

    if not unidade:
        unidade = UnidadeMercado(
            nome="Atacadao Rio Grande",
            rede_id=rede.id,
            cidade_id=cidade.id
        )
        db.add(unidade)
        db.commit()
        db.refresh(unidade)

    return unidade


def get_categoria(db, nome_categoria):
    return db.query(Categoria).filter_by(nome=nome_categoria).first()


def get_or_create_produto(db, nome, categoria_id):
    produto = db.query(Produto).filter_by(nome=nome).first()
    if not produto:
        produto = Produto(nome=nome, categoria_id=categoria_id)
        db.add(produto)
        db.commit()
        db.refresh(produto)
    elif produto.categoria_id != categoria_id:
        produto.categoria_id = categoria_id
    return produto


def salvar_preco(db, produto, unidade, valor):
    preco_db = db.query(PrecoProduto).filter_by(
        produto_id=produto.id,
        unidade_id=unidade.id
    ).first()

    if preco_db:
        preco_db.preco = valor
    else:
        db.add(PrecoProduto(
            produto_id=produto.id,
            unidade_id=unidade.id,
            preco=valor
        ))

    db.add(HistoricoPreco(
        produto_id=produto.id,
        unidade_id=unidade.id,
        preco=valor
    ))


def run():
    db = SessionLocal()
    unidade = get_contexto(db)

    vistos = set()
    total_salvos = 0
    total_bloqueados_categoria = 0
    total_ignorados_regra = 0

    for config in BUSCAS:
        print()
        print("=== BUSCA:", config["query"], "===")

        for page in range(1, 6):
            print("Pagina", page, "...")

            try:
                produtos = buscar_produtos(config["query"], page)
            except Exception as e:
                print("ERRO:", e)
                break

            if not produtos:
                print("Sem mais resultados.")
                break

            for item in produtos:
                nome = item.get("productName")
                preco = None

                pr = item.get("priceRange", {})
                if isinstance(pr, dict):
                    sp = pr.get("sellingPrice", {})
                    if isinstance(sp, dict):
                        preco = sp.get("lowPrice")

                if not nome or preco is None:
                    continue

                chave = normalizar(nome)
                if chave in vistos:
                    continue

                ok, motivo = relevante(
                    nome,
                    config["aceitar"],
                    config["bloquear"],
                    config["peso_min_g"]
                )

                if not ok:
                    total_ignorados_regra += 1
                    print(f"IGNORADO REGRA: {nome} -> {motivo}")
                    continue

                categoria_nome = classificar(nome)

                if categoria_nome not in CATEGORIAS_PERMITIDAS:
                    total_bloqueados_categoria += 1
                    print(f"BLOQUEADO CATEGORIA: {nome} -> {categoria_nome}")
                    continue

                categoria = get_categoria(db, categoria_nome)
                if not categoria:
                    print(f"ERRO: categoria nao encontrada no banco -> {categoria_nome}")
                    continue

                medida_valor, medida_unidade = extrair_medida(nome)
                produto = get_or_create_produto(db, nome, categoria.id)
                salvar_preco(db, produto, unidade, Decimal(str(preco)))

                vistos.add(chave)
                total_salvos += 1

                print(f"SALVO: {nome} | PRECO: {preco} | CATEGORIA: {categoria_nome} | MEDIDA: {medida_valor}{medida_unidade}")

    db.commit()
    db.close()

    print()
    print("===== RESUMO FINAL =====")
    print("TOTAL SALVOS:", total_salvos)
    print("TOTAL IGNORADOS REGRA:", total_ignorados_regra)
    print("TOTAL BLOQUEADOS CATEGORIA:", total_bloqueados_categoria)


if __name__ == "__main__":
    run()
