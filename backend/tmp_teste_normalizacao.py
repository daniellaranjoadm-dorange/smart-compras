from app.services.normalizacao_produto import gerar_assinatura_produto

exemplos = [
    "Arroz Extremo Sul Agulhinha - Tipo 1 5kg",
    "Arroz com Brócolis Swift Congelado 500g",
    "Arroz Carreteiro Swift 300g",
    "Mucilon Arroz e Aveia 230g",
    "Alimento Cães Baw Waw Méd. e Gde Carne, Fgo e Arroz 10,1kg",
    "Strogonoff de Frango Perdigão Cong Arroz e Champignon 300g",
    "Feijão Carioca Bulnez Tipo 1 1kg",
    "Feijão Tropeiro Swift 500g",
    "Café Jardim 500g",
    "Sandália Slim Square Havaianas 37/38 Café par",
    "Leite Longa Vida Aurora Integral Com Tampa 1L",
    "Bala Arcor Butter Toffees Leite 400g",
    "Papel Higiênico Bulnez Folha Dupla 30m 12 rolos",
]

for e in exemplos:
    print(e, "=>", gerar_assinatura_produto(e))
