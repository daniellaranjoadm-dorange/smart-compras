# -*- coding: utf-8 -*-
path = r".\app\services\normalizacao_produto.py"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# REMOVE filtro global de preparo (se existir)
content = content.replace(
'''    if contem_preparo(nome):
        return None

    peso = extrair_peso(nome)
''',
'''    peso = extrair_peso(nome)
'''
)

# GARANTE que feijao tenha filtro local (igual arroz)
content = content.replace(
'''    if " feijao " in base:
        if contem_preparo(nome):
            return None
        if contem_algum(base, EXCLUIR_FEIJAO):
            return None
        tipo = detectar_tipo(nome, TIPOS_FEIJAO)
        return f"feijao_{tipo or 'padrao'}_{peso or 'na'}"
''',
'''    if " feijao " in base:
        if contem_algum(base, EXCLUIR_FEIJAO):
            return None
        tipo = detectar_tipo(nome, TIPOS_FEIJAO)
        return f"feijao_{tipo or 'padrao'}_{peso or 'na'}"
'''
)

with open(path, "w", encoding="utf-8", newline="\n") as f:
    f.write(content)

print("PATCH_OK")
