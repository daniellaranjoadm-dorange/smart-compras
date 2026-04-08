# -*- coding: utf-8 -*-
from pathlib import Path

arquivos = [
    Path(r".\app\routes\comparacao.py"),
    Path(r".\app\routes\cesta.py"),
]

old = '''def dados_assinatura_do_produto(produto):
    assinatura_salva = getattr(produto, "assinatura", None)

    def montar(assinatura: str | None):
        if not assinatura:
            return None

        # formato novo: cafe_250g / feijao_carioca_1kg
        if "_" in assinatura and " | " not in assinatura:
            partes = assinatura.split("_")
            base = partes[0] if partes else None

            medida_valor = None
            medida_unidade = None

            for token in reversed(partes):
                m = re.match(r"^(\\d+(?:\\.\\d+)?)(kg|g|ml|l|m|rolos)$", token)
                if m:
                    try:
                        medida_valor = float(m.group(1))
                    except Exception:
                        medida_valor = None
                    medida_unidade = m.group(2)
                    break

            return assinatura, base, medida_valor, medida_unidade

        # formato legado: "base | 5g"
        if " | " in assinatura:
            partes = assinatura.split(" | ", 1)
            base = partes[0].strip()
            medida_txt = partes[1].strip() if len(partes) > 1 else ""

            medida_valor = None
            medida_unidade = None

            m = re.match(r"^(\\d+(?:\\.\\d+)?)(kg|g|ml|l|m|rolos)$", medida_txt)
            if m:
                try:
                    medida_valor = float(m.group(1))
                except Exception:
                    medida_valor = None
                medida_unidade = m.group(2)

            return assinatura, base, medida_valor, medida_unidade

        return None

    dados = montar(assinatura_salva)
    if dados:
        return dados

    assinatura_nova = gerar_assinatura_produto(produto.nome)
    dados = montar(assinatura_nova)
    if dados:
        return dados

    return assinatura_produto(produto.nome)
'''

new = '''def dados_assinatura_do_produto(produto):
    def montar(assinatura: str | None):
        if not assinatura:
            return None

        # formato novo: cafe_250g / feijao_carioca_1kg
        if "_" in assinatura and " | " not in assinatura:
            partes = assinatura.split("_")
            base = partes[0] if partes else None

            medida_valor = None
            medida_unidade = None

            for token in reversed(partes):
                m = re.match(r"^(\\d+(?:\\.\\d+)?)(kg|g|ml|l|m|rolos)$", token)
                if m:
                    try:
                        medida_valor = float(m.group(1))
                    except Exception:
                        medida_valor = None
                    medida_unidade = m.group(2)
                    break

            return assinatura, base, medida_valor, medida_unidade

        # formato legado: "base | 5g"
        if " | " in assinatura:
            partes = assinatura.split(" | ", 1)
            base = partes[0].strip()
            medida_txt = partes[1].strip() if len(partes) > 1 else ""

            medida_valor = None
            medida_unidade = None

            m = re.match(r"^(\\d+(?:\\.\\d+)?)(kg|g|ml|l|m|rolos)$", medida_txt)
            if m:
                try:
                    medida_valor = float(m.group(1))
                except Exception:
                    medida_valor = None
                medida_unidade = m.group(2)

            return assinatura, base, medida_valor, medida_unidade

        return None

    # PRIORIDADE TOTAL: core novo
    assinatura_nova = gerar_assinatura_produto(produto.nome)
    dados = montar(assinatura_nova)
    if dados:
        return dados

    # se o core novo disser que nao serve, ignora produto
    return None, None, None, None
'''

for path in arquivos:
    content = path.read_text(encoding="utf-8")
    if old not in content:
        raise SystemExit(f"Bloco alvo nao encontrado em {path}")
    content = content.replace(old, new)
    path.write_text(content, encoding="utf-8", newline="\n")
    print(f"[PATCH_OK] {path}")

print("PATCH_PRIORIDADE_CORE_OK")
