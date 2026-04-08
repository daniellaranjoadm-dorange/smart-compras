# -*- coding: utf-8 -*-
path = r".\app\services\normalizacao_produto.py"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
'''PALAVRAS_PREPARO = [
    " com ", " ao ", " aos ",
    "pronto", "pronta",
    "congelado", "congelada",
    "mistura", "tempero",
    "sabor", "molho",
    "carreteiro", "strogonoff",
    "sopinha", "refeicao", "refeição",
    "tropeiro", "cremoso"
]''',
'''PALAVRAS_PREPARO = [
    " ao ", " aos ",
    "pronto", "pronta",
    "congelado", "congelada",
    "mistura", "tempero",
    "sabor", "molho",
    "carreteiro", "strogonoff",
    "sopinha", "refeicao", "refeição",
    "tropeiro", "cremoso"
]'''
)

content = content.replace(
'''    if contem_preparo(nome):
        return None

    peso = extrair_peso(nome)

    if " arroz " in base:
        if contem_algum(base, EXCLUIR_ARROZ):
            return None
        tipo = detectar_tipo(nome, TIPOS_ARROZ)
        return f"arroz_{tipo or 'padrao'}_{peso or 'na'}"

    if " feijao " in base:
        if contem_algum(base, EXCLUIR_FEIJAO):
            return None
        tipo = detectar_tipo(nome, TIPOS_FEIJAO)
        return f"feijao_{tipo or 'padrao'}_{peso or 'na'}"
''',
'''    peso = extrair_peso(nome)

    if " arroz " in base:
        if contem_preparo(nome):
            return None
        if contem_algum(base, EXCLUIR_ARROZ):
            return None
        tipo = detectar_tipo(nome, TIPOS_ARROZ)
        return f"arroz_{tipo or 'padrao'}_{peso or 'na'}"

    if " feijao " in base:
        if contem_preparo(nome):
            return None
        if contem_algum(base, EXCLUIR_FEIJAO):
            return None
        tipo = detectar_tipo(nome, TIPOS_FEIJAO)
        return f"feijao_{tipo or 'padrao'}_{peso or 'na'}"
'''
)

with open(path, "w", encoding="utf-8", newline="\n") as f:
    f.write(content)

print("PATCH_OK")
