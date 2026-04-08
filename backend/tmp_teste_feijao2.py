from app.services.normalizacao_produto import gerar_assinatura_produto

exemplos = [
    "Feijão Carioca Bulnez Tipo 1 1kg",
    "Feijão Branco Da Terrinha Premium 500g",
    "Feijão Tropeiro Swift 500g",
]

for e in exemplos:
    print(e, "=>", gerar_assinatura_produto(e))
