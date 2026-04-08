# -*- coding: utf-8 -*-
import sqlite3
from collections import defaultdict

DB_PATH = "smart_compras.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# =========================
# 1. AGRUPAR PRODUTOS POR ASSINATURA
# =========================
cur.execute("SELECT id, assinatura FROM produtos WHERE assinatura IS NOT NULL")
rows = cur.fetchall()

grupos = defaultdict(list)

for pid, assinatura in rows:
    grupos[assinatura].append(pid)

total_grupos = 0
total_removidos = 0

# =========================
# 2. PROCESSAR GRUPOS DUPLICADOS
# =========================
for assinatura, ids in grupos.items():
    if len(ids) <= 1:
        continue

    total_grupos += 1

    principal = ids[0]
    duplicados = ids[1:]

    print(f"\n[GRUPO] assinatura={assinatura}")
    print(f"principal={principal} duplicados={duplicados}")

    for dup_id in duplicados:
        # mover preços
        cur.execute("""
            UPDATE precos
            SET produto_id = ?
            WHERE produto_id = ?
        """, (principal, dup_id))

        # deletar produto duplicado
        cur.execute("DELETE FROM produtos WHERE id = ?", (dup_id,))
        total_removidos += 1

# =========================
# 3. FINALIZAR
# =========================
conn.commit()
conn.close()

print("\n========== RESUMO DEDUP ==========")
print("Grupos processados:", total_grupos)
print("Produtos removidos:", total_removidos)
print("==================================")
