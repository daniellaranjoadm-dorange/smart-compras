# -*- coding: utf-8 -*-
from pathlib import Path

path = Path(r".\app\routes\comparacao.py")
content = path.read_text(encoding="utf-8")

if "def score_relevancia_comparacao(" not in content:
    helper = '''

def score_relevancia_comparacao(base: str, medida_valor, medida_unidade) -> float:
    if medida_valor is None or not medida_unidade:
        return 0.0

    alvo = None

    if base == "cafe":
        if medida_unidade == "g":
            alvo = 500
        elif medida_unidade == "kg":
            alvo = 0.5
    elif base == "feijao":
        if medida_unidade == "g":
            alvo = 1000
        elif medida_unidade == "kg":
            alvo = 1
    elif base == "arroz":
        if medida_unidade == "g":
            alvo = 5000
        elif medida_unidade == "kg":
            alvo = 5
    elif base == "leite":
        if medida_unidade == "ml":
            alvo = 1000
        elif medida_unidade == "l":
            alvo = 1

    if alvo is None:
        return 1.0

    return 100000.0 - abs(float(medida_valor) - float(alvo))


'''
    anchor = '@router.get("")'
    content = content.replace(anchor, helper + anchor, 1)

old_sort = '''    grupos_ordenados = sorted(
        grupos.values(),
        key=lambda g: (
            g["menor_preco"] if g["menor_preco"] is not None else 999999,
            g["assinatura"]
        )
    )
'''

new_sort = '''    grupos_ordenados = sorted(
        grupos.values(),
        key=lambda g: (
            -score_relevancia_comparacao(
                g.get("base"),
                g.get("medida_valor"),
                g.get("medida_unidade"),
            ),
            g["menor_preco"] if g["menor_preco"] is not None else 999999,
            g["assinatura"]
        )
    )
'''

if old_sort not in content:
    raise SystemExit("Bloco de ordenacao final nao encontrado em comparacao.py")

content = content.replace(old_sort, new_sort)

path.write_text(content, encoding="utf-8", newline="\n")
print("PATCH_RANKING_COMPARACAO_OK")
