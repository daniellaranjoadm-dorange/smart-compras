# -*- coding: utf-8 -*-
import re
from pathlib import Path

arquivos = [
    Path(r".\app\routes\comparacao.py"),
    Path(r".\app\routes\cesta.py"),
]

helper = '''
def dados_assinatura_do_produto(produto):
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

for path in arquivos:
    content = path.read_text(encoding="utf-8")

    if "def dados_assinatura_do_produto(produto):" not in content:
        if "def produto_bloqueado(" in content:
            content = content.replace(
                "def produto_bloqueado(",
                helper + "def produto_bloqueado(",
                1
            )
        else:
            raise SystemExit(f"Nao achei ponto de insercao em {path}")

    old_line = "assinatura, base, medida_valor, medida_unidade = assinatura_produto(produto.nome)"
    new_line = "assinatura, base, medida_valor, medida_unidade = dados_assinatura_do_produto(produto)"

    if old_line in content:
        content = content.replace(old_line, new_line)
    else:
        print(f"[AVISO] linha alvo nao encontrada em {path}")

    path.write_text(content, encoding="utf-8", newline="\n")
    print(f"[PATCH_OK] {path}")

print("PATCH_COMPARACAO_ASSINATURA_OK")
