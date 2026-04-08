# -*- coding: utf-8 -*-
from pathlib import Path

path = Path(r".\app\routes\cesta.py")
content = path.read_text(encoding="utf-8")

old = '''            atual = totais_por_unidade[chave]["itens"].get(item)
            if atual is None or oferta["preco"] < atual["preco"]:
                totais_por_unidade[chave]["itens"][item] = oferta
'''

new = '''            atual = totais_por_unidade[chave]["itens"].get(item)

            if atual is None:
                totais_por_unidade[chave]["itens"][item] = oferta
            else:
                score_atual = score_relevancia_item(
                    atual.get("base"),
                    atual.get("medida_valor"),
                    atual.get("medida_unidade"),
                )
                score_novo = score_relevancia_item(
                    oferta.get("base"),
                    oferta.get("medida_valor"),
                    oferta.get("medida_unidade"),
                )

                if (
                    score_novo > score_atual or
                    (score_novo == score_atual and oferta["preco"] < atual["preco"])
                ):
                    totais_por_unidade[chave]["itens"][item] = oferta
'''

if old not in content:
    raise SystemExit("Bloco de escolha por unidade nao encontrado.")

content = content.replace(old, new)

path.write_text(content, encoding="utf-8", newline="\n")
print("PATCH_MELHOR_MERCADO_OK")
