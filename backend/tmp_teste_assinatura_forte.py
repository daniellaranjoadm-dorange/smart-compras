from app.services.normalizacao_produto import gerar_assinatura_produto

exemplos = [
    "Farinha de Trigo Dona Benta Tipo 1 1kg",
    "Farinha de Trigo Integral Nita 1kg",
    "Farinha de Trigo Com Fermento Finna 1kg",
    "Café Melitta Torrado e Moído a Vácuo Tradicional 500g",
    "Café Solúvel 3 Corações Liofilizado 100g",
    "Café em Grãos Pilão Expresso 1kg",
    "Arroz Extremo Sul Agulhinha Tipo 1 5kg",
    "Feijão Carioca Bulnez Tipo 1 1kg",
    "Açúcar Cristal União 1kg",
    "Açúcar Orgânico Demerara 1kg",
]

for e in exemplos:
    print(e, "=>", gerar_assinatura_produto(e))
