# -*- coding: utf-8 -*-
from pathlib import Path

arquivos = [
    Path(r".\app\routes\comparacao.py"),
    Path(r".\app\routes\cesta.py"),
]

import_line = "from app.services.normalizacao_produto import gerar_assinatura_produto\n"

helper_old = '''def dados_assinatura_do_produto(produto):
    assinatura_salva = getattr(produto, "assinatura", None)

    if assinatura_salva:
        partes = assinatura_salva.split("_")
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

        return assinatura_salva, base, medida_valor, medida_unidade

    return assinatura_produto(produto.nome)
'''

helper_new = '''def dados_assinatura_do_produto(produto):
    assinatura_salva = getattr(produto, "assinatura", None)

    def montar(assinatura: str | None):
        if not assinatura:
            return None

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

    dados = montar(assinatura_salva)
    if dados:
        return dados

    assinatura_nova = gerar_assinatura_produto(produto.nome)
    dados = montar(assinatura_nova)
    if dados:
        return dados

    return assinatura_produto(produto.nome)
'''

for path in arquivos:
    content = path.read_text(encoding="utf-8")

    if "from app.services.normalizacao_produto import gerar_assinatura_produto" not in content:
        if content.startswith("from "):
            content = import_line + content
        else:
            content = import_line + content

    if helper_old in content:
        content = content.replace(helper_old, helper_new)
    else:
        print(f"[AVISO] helper_old nao encontrado exatamente em {path}")

    path.write_text(content, encoding="utf-8", newline="\n")
    print(f"[PATCH_OK] {path}")

print("PATCH_FALLBACK_CORE_OK")
