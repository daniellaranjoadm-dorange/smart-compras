from app.services.normalizacao_produto import gerar_assinatura_produto

exemplos = [
    "Água Mineral Bonafont Sem gás 500ml",
    "Água Mineral Bonafont Com gás 1,5L",
    "Molho de Tomate Quero Tradicional 300g",
    "Molho de Tomate Heinz Manjericão 300g",
    "Molho de Tomate Quero Pizza 340g",
    "Extrato de Tomate Elefante 300g",
    "Pasta de Amendoim Integral 500g",
    "Pasta de Amendoim Crunchy 1,005kg",
]

for e in exemplos:
    print(e, "=>", gerar_assinatura_produto(e))
