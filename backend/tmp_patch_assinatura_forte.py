# -*- coding: utf-8 -*-
path = r".\app\services\normalizacao_produto.py"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# =========================
# INJETAR HELPERS DE ATRIBUTO
# =========================
helpers = '''

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
'''

if "def detectar_atributos(nome: str)" not in content:
    anchor = "def gerar_assinatura_produto(nome: str):"
    if anchor not in content:
        raise SystemExit("Funcao gerar_assinatura_produto nao encontrada")
    content = content.replace(anchor, helpers + "\n\ndef gerar_assinatura_produto(nome: str):", 1)

# =========================
# TROCAR RETORNOS POR compor_assinatura
# =========================
replacements = {
    '''        return f"arroz_{tipo}_{medida}"''':
    '''        return compor_assinatura(f"arroz_{tipo}", nome, medida)''',

    '''        return f"feijao_{tipo}_{medida}"''':
    '''        return compor_assinatura(f"feijao_{tipo}", nome, medida)''',

    '''        return f"cafe_{medida}"''':
    '''        return compor_assinatura("cafe", nome, medida)''',

    '''        return f"acucar_{tipo}_{medida}"''':
    '''        return compor_assinatura(f"acucar_{tipo}", nome, medida)''',

    '''        return f"farinha_{tipo}_{medida}"''':
    '''        return compor_assinatura(f"farinha_{tipo}", nome, medida)''',
}

for old, new in replacements.items():
    if old in content:
        content = content.replace(old, new)

with open(path, "w", encoding="utf-8", newline="\n") as f:
    f.write(content)

print("PATCH_ASSINATURA_FORTE_OK")
