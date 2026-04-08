# -*- coding: utf-8 -*-
from pathlib import Path

# =========================
# PATCH EM cesta.py
# =========================
path_cesta = Path(r".\app\routes\cesta.py")
content = path_cesta.read_text(encoding="utf-8")

if "def score_relevancia_item(" not in content:
    helper = '''

def score_relevancia_item(base: str, medida_valor, medida_unidade) -> float:
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
    anchor = "def produto_valido_para_item("
    if anchor in content:
        content = content.replace(anchor, helper + anchor, 1)
    else:
        raise SystemExit("Nao achei ponto de insercao em cesta.py")

old_sort = '''        candidatos.sort(key=lambda x: x["preco"])
'''
new_sort = '''        candidatos.sort(
            key=lambda x: (
                -score_relevancia_item(
                    x.get("base"),
                    x.get("medida_valor"),
                    x.get("medida_unidade"),
                ),
                x["preco"],
            )
        )
'''
if old_sort in content:
    content = content.replace(old_sort, new_sort)
else:
    print("[AVISO] sort de candidatos nao encontrado em cesta.py")

path_cesta.write_text(content, encoding="utf-8", newline="\n")
print("[PATCH_OK] cesta.py")

# =========================
# PATCH EM comparacao.py
# =========================
path_comp = Path(r".\app\routes\comparacao.py")
content = path_comp.read_text(encoding="utf-8")

old_filter = '''        if medida_valor is None:
            continue
'''
new_filter = '''        if not assinatura or not base:
            continue
'''
if old_filter in content:
    content = content.replace(old_filter, new_filter)
else:
    print("[AVISO] filtro medida_valor nao encontrado em comparacao.py")

path_comp.write_text(content, encoding="utf-8", newline="\n")
print("[PATCH_OK] comparacao.py")

print("PATCH_RELEVANCIA_OK")
