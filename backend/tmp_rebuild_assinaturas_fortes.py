# -*- coding: utf-8 -*-
import sqlite3
from app.services.normalizacao_produto import gerar_assinatura_produto

DB_PATH = "smart_compras.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("SELECT id, nome, assinatura FROM produtos")
rows = cur.fetchall()

total = 0
atualizados = 0
sem_assinatura = 0

for produto_id, nome, assinatura_atual in rows:
    total += 1
    assinatura_nova = gerar_assinatura_produto(nome)

    if not assinatura_nova or assinatura_nova.endswith("_na"):
        sem_assinatura += 1
        continue

    if assinatura_atual == assinatura_nova:
        continue

    cur.execute(
        "UPDATE produtos SET assinatura = ? WHERE id = ?",
        (assinatura_nova, produto_id),
    )
    atualizados += 1
    print(f"[UPDATE] id={produto_id} assinatura={assinatura_nova}")

conn.commit()
conn.close()

print("========== RESUMO REBUILD ==========")
print("Produtos lidos:", total)
print("Assinaturas atualizadas:", atualizados)
print("Sem assinatura utilizavel:", sem_assinatura)
print("====================================")
