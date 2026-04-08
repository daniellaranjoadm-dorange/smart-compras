# -*- coding: utf-8 -*-
from pathlib import Path

path = Path(r".\app\services\normalizacao_produto.py")
content = path.read_text(encoding="utf-8")

old = '''    if " sabao " in base or " sabão " in nome.lower():
        if contem_algum(base, EXCLUIR_SABAO):
            return None
        tipo = detectar_tipo(nome, TIPOS_SABAO)
        mult = "na"
        m = re.search(r"(\\d+)\\s*x\\s*(\\d+)\\s*g", base)
        if m:
            mult = f"{m.group(1)}x{m.group(2)}g"
        if mult != "na":
            return f"sabao_{tipo}_{mult}"
        return f"sabao_{tipo}_{medida}" if medida != "na" else f"sabao_{tipo}"

    tokens = [t for t in base.strip().split() if t]
    if tokens:
        return tokens[0]

    return None
'''

new = '''    if " agua " in base:
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
            elif " passata " in base:
                tipo = "passata"
            elif " hot dog " in base or " dogao " in base:
                tipo = "hotdog"
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
        elif " cacau " in base:
            tipo = "cacau"
        elif " avela " in base:
            tipo = "avela"
        else:
            tipo = "padrao"
        return f"pasta_amendoim_{tipo}_{medida}" if medida != "na" else f"pasta_amendoim_{tipo}"

    if " sabao " in base or " sabão " in nome.lower():
        if contem_algum(base, EXCLUIR_SABAO):
            return None
        tipo = detectar_tipo(nome, TIPOS_SABAO)
        mult = "na"
        m = re.search(r"(\\d+)\\s*x\\s*(\\d+)\\s*g", base)
        if m:
            mult = f"{m.group(1)}x{m.group(2)}g"
        if mult != "na":
            return f"sabao_{tipo}_{mult}"
        return f"sabao_{tipo}_{medida}" if medida != "na" else f"sabao_{tipo}"

    return None
'''

if old not in content:
    raise SystemExit("Bloco final da funcao nao encontrado.")

content = content.replace(old, new)

path.write_text(content, encoding="utf-8", newline="\n")
print("PATCH_NORMALIZACAO_GENERICOS_OK")
