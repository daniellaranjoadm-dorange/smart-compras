# -*- coding: utf-8 -*-
from pathlib import Path

path = Path(r".\app\services\normalizacao_produto.py")
lines = path.read_text(encoding="utf-8").splitlines()

start = None
end = None

# localizar inicio da funcao
for i, line in enumerate(lines):
    if line.strip().startswith("def gerar_assinatura_produto"):
        start = i
        break

if start is None:
    raise SystemExit("FUNCAO NAO ENCONTRADA")

# localizar fim (proxima funcao ou EOF)
for i in range(start + 1, len(lines)):
    if lines[i].startswith("def "):
        end = i
        break

if end is None:
    end = len(lines)

# nova funcao forte
nova_funcao = """
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
""".strip("\n").splitlines()

# substituir bloco
novo_conteudo = lines[:start] + nova_funcao + lines[end:]

path.write_text("\n".join(novo_conteudo), encoding="utf-8")

print("PATCH_FUNCAO_ASSINATURA_OK")
