# -*- coding: utf-8 -*-
import re
import unicodedata

PALAVRAS_RUIDO = [
    "biscoito", "chocolate", "doce", "capsula", "cápsula",
    "ração", "racao", "desodorante", "concha",
    "iogurte", "bebida", "alcoolica", "alcoólica",
    "condensado", "creme de leite", "doce de leite",
    "soro de leite", "leite vegano", "cappuccino",
    "energético", "energetico", "refrigerante", "cerveja",
    "havaianas", "sandalia", "sandália", "porta escova",
]

PALAVRAS_PREPARO = [
    " ao ", " aos ",
    "pronto", "pronta",
    "congelado", "congelada",
    "mistura", "tempero",
    "sabor", "molho",
    "carreteiro", "strogonoff",
    "sopinha", "refeicao", "refeição",
    "tropeiro", "cremoso"
]

TIPOS_ARROZ = ["agulhinha", "parboilizado", "integral", "branco"]
TIPOS_FEIJAO = ["carioca", "preto", "branco", "fradinho", "jalo", "rajado"]
TIPOS_MACARRAO = ["espaguete", "spaghetti", "penne", "parafuso", "fusilli", "ninho", "argolinha", "ave maria", "gravata"]
TIPOS_ACUCAR = ["refinado", "cristal", "demerara", "mascavo", "confeiteiro"]
TIPOS_OLEO = ["soja", "milho", "girassol", "canola", "coco", "algodao", "algodão", "composto"]
TIPOS_FARINHA = ["trigo", "mandioca", "milho", "rosca", "aveia"]
TIPOS_SABAO = ["po", "pó", "liquido", "líquido", "barra", "pedaco", "pedaço"]

EXCLUIR_ARROZ = [
    "ração", "racao", "vinagre", "macarrao", "macarrão", "biscoito",
    "porta", "cachorro", "gato", "tempero", "mucilon", "alimento",
    "frango", "feijoada", "palmito", "brocolis", "brócolis", "swift"
]

EXCLUIR_FEIJAO = [
    "concha", "pronto", "caldo", "tropeiro", "feijoada"
]

EXCLUIR_CAFE = [
    "sandalia", "sandália", "capsula", "capsulas", "cápsula", "cápsulas",
    "chocolate", "havaianas"
]

EXCLUIR_LEITE = [
    "chocolate", "ovo", "biscoito", "doce", "pudim",
    "fermentado", "bala", "pão", "pao", "sobremesa",
    "vegetal", "notmilk", "soja"
]

EXCLUIR_MACARRAO = [
    "instantaneo", "instantâneo", "lamen", "lámen", "hot bowls",
    "harusame", "yakissoba", "vagem"
]

EXCLUIR_OLEO = [
    "lubrificante", "desengripante", "banana", "serum", "sérum",
    "capilar", "shampoo", "condicionador", "creme", "air fryer",
    "fritadeira", "desengordurante", "motor",
    "atum", "sardinha", "peixe", "enlatado",
    "banho", "corpo", "pele", "cosmetico", "cosmético",
    "sabonete"
]

EXCLUIR_ACUCAR = [
    "acai", "açaí", "adocante", "adoçante", "zero", "diet"
]

EXCLUIR_FARINHA = [
    "farofa", "mix", "pizza", "empanar"
]

EXCLUIR_SABAO = [
    "lava roupas", "lava-roupas", "detergente", "lava loucas", "lava-louças",
    "mon bijou", "brilhante", "omo", "tixan", "surf", "coquel"
]


def normalizar_texto(texto: str) -> str:
    texto = texto or ""
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = texto.lower()
    texto = re.sub(r"[^a-z0-9]+", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return f" {texto} "


def contem_ruido(nome: str) -> bool:
    base = normalizar_texto(nome)
    return any(normalizar_texto(p).strip() in base for p in PALAVRAS_RUIDO)


def contem_preparo(nome: str) -> bool:
    base = normalizar_texto(nome)
    return any(normalizar_texto(p).strip() in base for p in PALAVRAS_PREPARO)


def contem_algum(base: str, termos: list[str]) -> bool:
    return any(normalizar_texto(t).strip() in base for t in termos)


def detectar_tipo(nome: str, tipos: list[str]) -> str:
    base = normalizar_texto(nome)
    for t in tipos:
        if normalizar_texto(t).strip() in base:
            return normalizar_texto(t).strip().replace(" ", "_")
    return "padrao"


def extrair_peso_ou_volume(nome: str) -> str:
    texto = nome.lower()

    # MULTIPACK primeiro
    m = re.search(r"(\d+)\s*x\s*(\d+)\s*(g|ml)", texto)
    if m:
        qtd = m.group(1)
        valor = m.group(2)
        unidade = m.group(3)
        return f"{qtd}x{valor}{unidade}"

    # PEGAR TODOS OS MATCHES E ESCOLHER O MAIOR
    matches = re.findall(r"(\d+(?:[.,]\d+)?)\s*(kg|g|ml|l)", texto)

    if matches:
        def peso_em_gramas(valor, unidade):
            v = float(valor.replace(",", "."))
            if unidade == "kg":
                return v * 1000
            if unidade == "g":
                return v
            if unidade == "l":
                return v * 1000
            if unidade == "ml":
                return v
            return v

        melhor = max(matches, key=lambda x: peso_em_gramas(x[0], x[1]))

        valor = melhor[0].replace(",", ".")
        unidade = melhor[1]

        valor = format(float(valor), "g") if "." in valor else valor

        return f"{valor}{unidade}"

    return "na"


def extrair_metragem(nome: str) -> str:
    base = normalizar_texto(nome).strip()
    m = re.search(r"(\d+)\s*m\b", base)
    if m:
        return f"{m.group(1)}m"
    return "na"


def extrair_rolos(nome: str) -> str:
    base = normalizar_texto(nome).strip()
    m = re.search(r"(\d+)\s*(rolos|rolo|un|unidades)\b", base)
    if m:
        return f"{m.group(1)}rolos"
    return "na"


def detectar_folha(nome: str) -> str:
    base = normalizar_texto(nome)
    if " folha dupla " in base:
        return "folha_dupla"
    if " folha simples " in base:
        return "folha_simples"
    if " folha tripla " in base:
        return "folha_tripla"
    if " fs " in base:
        return "folha_simples"
    if " fd " in base:
        return "folha_dupla"
    return "folha_na"




def detectar_atributos(nome: str) -> list[str]:
    base = normalizar_texto(nome)
    attrs = []

    # tipo numerico
    if " tipo 1 " in base or " tipo i " in base:
        attrs.append("tipo1")
    elif " tipo 2 " in base or " tipo ii " in base:
        attrs.append("tipo2")
    elif " tipo 00 " in base:
        attrs.append("tipo00")

    # farinha
    if " integral " in base:
        attrs.append("integral")
    if " com fermento " in base:
        attrs.append("com_fermento")
    if " sem fermento " in base:
        attrs.append("sem_fermento")

    # cafe
    if " soluvel " in base or " solúvel " in nome.lower():
        attrs.append("soluvel")
    if " em graos " in base or " em graos " in normalizar_texto(nome):
        attrs.append("graos")
    if " torrado e moido " in base or " torrado moido " in base:
        attrs.append("torrado_moido")
    if " descafeinado " in base:
        attrs.append("descafeinado")
    if " com leite " in base:
        attrs.append("com_leite")

    # acucar
    if " organico " in base or " orgânico " in nome.lower():
        attrs.append("organico")

    return attrs


def compor_assinatura(base_nome: str, nome: str, medida: str) -> str:
    attrs = detectar_atributos(nome)
    partes = [base_nome] + attrs + [medida]
    partes = [p for p in partes if p and p != "na"]
    return "_".join(partes)


def gerar_assinatura_produto(nome: str):
    base = normalizar_texto(nome)

    if contem_ruido(nome):
        return None

    medida = extrair_peso_ou_volume(nome)

    if " agua " in base:
        gas = "com_gas" if " com gas " in base else "sem_gas"
        return f"agua_{gas}_{medida}" if medida != "na" else f"agua_{gas}"

    if " molho " in base:
        if " tomate " in base:
            if " manjericao " in base:
                tipo = "manjericao"
            elif " bolonhesa " in base:
                tipo = "bolonhesa"
            elif " pizza " in base:
                tipo = "pizza"
            else:
                tipo = "tradicional"
            return f"molho_tomate_{tipo}_{medida}" if medida != "na" else f"molho_tomate_{tipo}"
        return None

    if " extrato " in base and " tomate " in base:
        return f"extrato_tomate_{medida}" if medida != "na" else "extrato_tomate"

    if " pasta de amendoim " in base:
        if " integral " in base:
            tipo = "integral"
        elif " crocante " in base or " crunchy " in base:
            tipo = "crocante"
        else:
            tipo = "padrao"
        return f"pasta_amendoim_{tipo}_{medida}" if medida != "na" else f"pasta_amendoim_{tipo}"

    # fallback CONTROLADO (não destrutivo)
    tokens = [t for t in base.strip().split() if t]
    if len(tokens) >= 2:
        return "_".join(tokens[:2])

    return None