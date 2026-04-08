from app.services.normalizacao_produto import gerar_assinatura_produto

exemplos = [
    "Feijão Carioca Bulnez Tipo 1 1kg",
    "Feijão Tropeiro Swift 500g",
    "Leite Longa Vida Aurora Integral Com Tampa 1L",
    "Arroz com Brócolis Swift Congelado 500g",
    "Arroz Extremo Sul Agulhinha - Tipo 1 5kg",
]

for e in exemplos:
    print(e, "=>", gerar_assinatura_produto(e))
