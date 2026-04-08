from app.services.normalizacao_produto import gerar_assinatura_produto

exemplos = [
    "Arroz Extremo Sul Agulhinha Tipo 1 5kg",
    "Feijão Carioca Bulnez Tipo 1 1kg",
    "Café Gourmet Melitta Torra da Rainha 250g",
    "Leite Longa Vida Aurora Integral Com Tampa 1L",
    "Papel Higiênico Bulnez Folha Dupla 30m 12 rolos",
    "Macarrão com Ovos Camil Espaguete 500g",
    "Macarrão Grano Duro Baronia Fusilli 500g",
    "Óleo de Soja Soya 900ml",
    "Óleo Lubrificante Ipiranga 5W30 1L",
    "Sardinha Sulpesca Óleo Comestível 75g",
    "Óleo Vegetal Sebella Fry 14,5kg",
    "Açúcar Refinado Globo 1kg",
    "Açaí Frooty 1,5L",
    "Farinha de Trigo Nita 5kg",
    "Farofa de Mandioca Yoki 200g",
    "Sabão em Pedaço Ypê Neutro 5x160g",
    "Lava Roupas Líquido Omo 3L"
]

for e in exemplos:
    print(e, "=>", gerar_assinatura_produto(e))
