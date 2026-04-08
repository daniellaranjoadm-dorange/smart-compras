from app.services.normalizacao_produto import gerar_assinatura_produto

exemplos = [
    "Arroz",
    "Feijão",
    "Café",
    "Açúcar",
    "Farinha",
    "Macarrão",
    "Óleo",
    "Leite",
]

for e in exemplos:
    print(e, "=>", gerar_assinatura_produto(e))
