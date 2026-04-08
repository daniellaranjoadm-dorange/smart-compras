# -*- coding: utf-8 -*-
from pathlib import Path
import re

# =========================
# PATCH CESTA
# =========================
path_cesta = Path(r".\app\routes\cesta.py")
content = path_cesta.read_text(encoding="utf-8")

old_helper = '''def score_relevancia_item(base: str, medida_valor, medida_unidade) -> float:
    if medida_valor is None or not medida_unidade:
        return 0.0

    alvo = None

    if base == "cafe" and medida_unidade == "g":
        alvo = 500
    elif base == "feijao" and medida_unidade == "kg":
        alvo = 1
    elif base == "arroz" and medida_unidade == "kg":
        alvo = 5
    elif base == "leite" and medida_unidade == "l":
        alvo = 1
    elif base == "acucar" and medida_unidade == "kg":
        alvo = 1
    elif base == "oleo" and medida_unidade == "ml":
        alvo = 900

    if alvo is None:
        return 1.0

    return 1000.0 - abs(float(medida_valor) - float(alvo))
'''

new_helper = '''def score_relevancia_item(base: str, medida_valor, medida_unidade) -> float:
    if medida_valor is None or not medida_unidade:
        return 0.0

    alvo = None

    if base == "cafe":
        if medida_unidade == "g":
            alvo = 500
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
    elif base == "acucar":
        if medida_unidade == "g":
            alvo = 1000
        elif medida_unidade == "kg":
            alvo = 1
    elif base == "oleo":
        if medida_unidade == "ml":
            alvo = 900
        elif medida_unidade == "l":
            alvo = 0.9

    if alvo is None:
        return 1.0

    return 100000.0 - abs(float(medida_valor) - float(alvo))
'''

if old_helper in content:
    content = content.replace(old_helper, new_helper)
else:
    print("[AVISO] helper antigo nao encontrado em cesta.py")

# reforçar ordenação por relevância + preço em qualquer sort simples de candidatos
content = content.replace(
'''        candidatos.sort(key=lambda x: x["preco"])''',
'''        candidatos.sort(
            key=lambda x: (
                -score_relevancia_item(
                    x.get("base"),
                    x.get("medida_valor"),
                    x.get("medida_unidade"),
                ),
                x["preco"],
            )
        )'''
)

# reforçar ordenação de ofertas por mercado
content = content.replace(
'''            ofertas_item.sort(key=lambda x: x["preco"])''',
'''            ofertas_item.sort(
                key=lambda x: (
                    -score_relevancia_item(
                        x.get("base"),
                        x.get("medida_valor"),
                        x.get("medida_unidade"),
                    ),
                    x["preco"],
                )
            )'''
)

path_cesta.write_text(content, encoding="utf-8", newline="\n")
print("[PATCH_OK] cesta.py")

# =========================
# PATCH COMPARACAO
# =========================
path_comp = Path(r".\app\routes\comparacao.py")
content = path_comp.read_text(encoding="utf-8")

# afrouxar filtro para base bater com query
content = content.replace(
'''        if not assinatura or not base:
            continue''',
'''        if not assinatura or not base:
            continue'''
)

# substituir filtro de tokens legado por base simples, se existir
content = content.replace(
'''        if not any(token in assinatura.lower() for token in tokens_q):
            continue''',
'''        if not any(token in (base or "").lower() for token in tokens_q):
            continue'''
)

content = content.replace(
'''        if not any(token in base.lower() for token in tokens_q):
            continue''',
'''        if not any(token in (base or "").lower() for token in tokens_q):
            continue'''
)

path_comp.write_text(content, encoding="utf-8", newline="\n")
print("[PATCH_OK] comparacao.py")

print("PATCH_RELEVANCIA_FINAL_OK")
