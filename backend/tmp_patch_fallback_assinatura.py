# -*- coding: utf-8 -*-
from pathlib import Path

path = Path(r".\app\services\normalizacao_produto.py")
content = path.read_text(encoding="utf-8")

old = '''def gerar_assinatura_produto(nome: str):
    base = normalizar_texto(nome)

    if contem_ruido(nome):
        return None

    medida = extrair_peso_ou_volume(nome)

    if " arroz " in base:
        if contem_preparo(nome) or contem_algum(base, EXCLUIR_ARROZ):
            return None
        tipo = detectar_tipo(nome, TIPOS_ARROZ)
        return compor_assinatura(f"arroz_{tipo}", nome, medida)

    if " feijao " in base:
        if contem_algum(base, EXCLUIR_FEIJAO):
            return None
        tipo = detectar_tipo(nome, TIPOS_FEIJAO)
        return compor_assinatura(f"feijao_{tipo}", nome, medida)

    if " cafe " in base:
        if contem_algum(base, EXCLUIR_CAFE):
            return None
        return compor_assinatura("cafe", nome, medida)

    if " leite " in base:
        if contem_algum(base, EXCLUIR_LEITE):
            return None
        return f"leite_{medida}"

    if " papel higienico " in base:
        folha = detectar_folha(nome)
        metragem = extrair_metragem(nome)
        rolos = extrair_rolos(nome)
        return f"papel_higienico_{folha}_{metragem}_{rolos}"

    if " macarrao " in base or " espaguete " in base or " spaghetti " in base or " penne " in base or " parafuso " in base or " fusilli " in base:
        if contem_algum(base, EXCLUIR_MACARRAO):
            return None
        tipo = detectar_tipo(nome, TIPOS_MACARRAO)
        return f"macarrao_{tipo}_{medida}"

    if " oleo " in base:
        if contem_algum(base, EXCLUIR_OLEO):
            return None
        tipo = detectar_tipo(nome, TIPOS_OLEO)
        return f"oleo_{tipo}_{medida}"

    if " acucar " in base:
        if contem_algum(base, EXCLUIR_ACUCAR):
            return None
        tipo = detectar_tipo(nome, TIPOS_ACUCAR)
        return compor_assinatura(f"acucar_{tipo}", nome, medida)

    if " farinha " in base:
        if contem_algum(base, EXCLUIR_FARINHA):
            return None
        tipo = detectar_tipo(nome, TIPOS_FARINHA)
        return compor_assinatura(f"farinha_{tipo}", nome, medida)

    if " sabao " in base or " sabão " in nome.lower():
        if contem_algum(base, EXCLUIR_SABAO):
            return None
        tipo = detectar_tipo(nome, TIPOS_SABAO)
        mult = "na"
        m = re.search(r"(\\d+)\\s*x\\s*(\\d+)\\s*g", base)
        if m:
            mult = f"{m.group(1)}x{m.group(2)}g"
        return f"sabao_{tipo}_{mult if mult != 'na' else medida}"

    return None
'''

new = '''def gerar_assinatura_produto(nome: str):
    base = normalizar_texto(nome)

    if contem_ruido(nome):
        return None

    medida = extrair_peso_ou_volume(nome)

    def sem_medida(prefixo: str) -> str:
        return prefixo

    if " arroz " in base:
        if contem_preparo(nome) or contem_algum(base, EXCLUIR_ARROZ):
            return None
        tipo = detectar_tipo(nome, TIPOS_ARROZ)
        return compor_assinatura(f"arroz_{tipo}", nome, medida) if medida != "na" else sem_medida(f"arroz_{tipo}")

    if " feijao " in base:
        if contem_algum(base, EXCLUIR_FEIJAO):
            return None
        tipo = detectar_tipo(nome, TIPOS_FEIJAO)
        return compor_assinatura(f"feijao_{tipo}", nome, medida) if medida != "na" else sem_medida(f"feijao_{tipo}")

    if " cafe " in base:
        if contem_algum(base, EXCLUIR_CAFE):
            return None
        return compor_assinatura("cafe", nome, medida) if medida != "na" else sem_medida("cafe")

    if " leite " in base:
        if contem_algum(base, EXCLUIR_LEITE):
            return None
        return f"leite_{medida}" if medida != "na" else "leite"

    if " papel higienico " in base:
        folha = detectar_folha(nome)
        metragem = extrair_metragem(nome)
        rolos = extrair_rolos(nome)
        assinatura = f"papel_higienico_{folha}_{metragem}_{rolos}"
        return assinatura.replace("_na_na", "").replace("_na", "")

    if " macarrao " in base or " espaguete " in base or " spaghetti " in base or " penne " in base or " parafuso " in base or " fusilli " in base:
        if contem_algum(base, EXCLUIR_MACARRAO):
            return None
        tipo = detectar_tipo(nome, TIPOS_MACARRAO)
        return f"macarrao_{tipo}_{medida}" if medida != "na" else f"macarrao_{tipo}"

    if " oleo " in base:
        if contem_algum(base, EXCLUIR_OLEO):
            return None
        tipo = detectar_tipo(nome, TIPOS_OLEO)
        return f"oleo_{tipo}_{medida}" if medida != "na" else f"oleo_{tipo}"

    if " acucar " in base:
        if contem_algum(base, EXCLUIR_ACUCAR):
            return None
        tipo = detectar_tipo(nome, TIPOS_ACUCAR)
        return compor_assinatura(f"acucar_{tipo}", nome, medida) if medida != "na" else sem_medida(f"acucar_{tipo}")

    if " farinha " in base:
        if contem_algum(base, EXCLUIR_FARINHA):
            return None
        tipo = detectar_tipo(nome, TIPOS_FARINHA)
        return compor_assinatura(f"farinha_{tipo}", nome, medida) if medida != "na" else sem_medida(f"farinha_{tipo}")

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

    tokens = [t for t in base.strip().split() if t]
    if tokens:
        return tokens[0]

    return None
'''

if old not in content:
    raise SystemExit("Bloco da funcao nao encontrado exatamente.")

content = content.replace(old, new)
path.write_text(content, encoding="utf-8", newline="\n")
print("PATCH_FALLBACK_ASSINATURA_OK")
