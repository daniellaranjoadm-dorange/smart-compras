# -*- coding: utf-8 -*-
path = r".\app\services\normalizacao_produto.py"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

insert_rules = """

EXCLUIR_ARROZ = [
    "ração", "racao", "vinagre", "macarrao", "biscoito",
    "porta", "cachorro", "gato", "tempero"
]

EXCLUIR_FEIJAO = [
    "concha", "pronto", "caldo"
]

EXCLUIR_CAFE = [
    "sandalia", "capsula", "capsulas"
]

EXCLUIR_LEITE = [
    "chocolate", "ovo", "biscoito", "doce", "pudim"
]
"""

if "EXCLUIR_ARROZ" not in content:
    content = content.replace("TIPOS_FEIJAO =", insert_rules + "\nTIPOS_FEIJAO =")

def patch_categoria(bloco, exclusoes):
    lines = bloco.split("\n")
    new_lines = []
    for line in lines:
        new_lines.append(line)
        if 'if "' in line and 'in base' in line:
            new_lines.append(f"        if any(p in base for p in {exclusoes}): return None")
    return "\n".join(new_lines)

content = content.replace(
    'if "arroz" in base:',
    'if "arroz" in base:\n        if any(p in base for p in EXCLUIR_ARROZ): return None'
)

content = content.replace(
    'if "feijao" in base:',
    'if "feijao" in base:\n        if any(p in base for p in EXCLUIR_FEIJAO): return None'
)

content = content.replace(
    'if "cafe" in base:',
    'if "cafe" in base:\n        if any(p in base for p in EXCLUIR_CAFE): return None'
)

content = content.replace(
    'if "leite" in base:',
    'if "leite" in base:\n        if any(p in base for p in EXCLUIR_LEITE): return None'
)

with open(path, "w", encoding="utf-8", newline="\n") as f:
    f.write(content)

print("PATCH_OK")
