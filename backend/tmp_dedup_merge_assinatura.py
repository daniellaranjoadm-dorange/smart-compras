# -*- coding: utf-8 -*-
import sqlite3
from collections import defaultdict

DB_PATH = "smart_compras.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# =========================
# 1. CARREGAR PRODUTOS COM ASSINATURA
# =========================
cur.execute("""
    SELECT id, nome, assinatura
    FROM produtos
    WHERE assinatura IS NOT NULL
      AND TRIM(assinatura) <> ''
""")
produtos = cur.fetchall()

# quantidade de preços por produto
cur.execute("""
    SELECT produto_id, COUNT(*)
    FROM precos
    GROUP BY produto_id
""")
contagem_precos = {produto_id: qtd for produto_id, qtd in cur.fetchall()}

grupos = defaultdict(list)
for produto_id, nome, assinatura in produtos:
    grupos[assinatura].append({
        "id": produto_id,
        "nome": nome,
        "assinatura": assinatura,
        "qtd_precos": contagem_precos.get(produto_id, 0),
    })

# =========================
# 2. DEDUP + MERGE DE PREÇOS
# =========================
grupos_processados = 0
produtos_removidos = 0
precos_movidos = 0
precos_descartados = 0

for assinatura, itens in grupos.items():
    if len(itens) <= 1:
        continue

    grupos_processados += 1

    # produto principal = mais preços; empate = menor id
    itens_ordenados = sorted(
        itens,
        key=lambda x: (-x["qtd_precos"], x["id"])
    )
    principal = itens_ordenados[0]
    duplicados = itens_ordenados[1:]

    print(f"\n[GRUPO] assinatura={assinatura}")
    print(f"  principal: id={principal['id']} precos={principal['qtd_precos']} nome={principal['nome']}")

    for dup in duplicados:
        dup_id = dup["id"]
        print(f"  duplicado: id={dup_id} precos={dup['qtd_precos']} nome={dup['nome']}")

        # carregar preços do duplicado
        cur.execute("""
            SELECT id, unidade_id, preco
            FROM precos
            WHERE produto_id = ?
        """, (dup_id,))
        precos_dup = cur.fetchall()

        for preco_id, unidade_id, valor in precos_dup:
            # já existe preço do principal nessa unidade?
            cur.execute("""
                SELECT id, preco
                FROM precos
                WHERE produto_id = ? AND unidade_id = ?
                ORDER BY id
                LIMIT 1
            """, (principal["id"], unidade_id))
            existente = cur.fetchone()

            if existente:
                # já existe preço no principal -> descarta o duplicado
                cur.execute("DELETE FROM precos WHERE id = ?", (preco_id,))
                precos_descartados += 1
                print(f"    [DESCARTA_PRECO] preco_id={preco_id} unidade_id={unidade_id} valor={valor}")
            else:
                # move o preço para o principal
                cur.execute("""
                    UPDATE precos
                    SET produto_id = ?
                    WHERE id = ?
                """, (principal["id"], preco_id))
                precos_movidos += 1
                print(f"    [MOVE_PRECO] preco_id={preco_id} unidade_id={unidade_id} valor={valor}")

        # apagar produto duplicado
        cur.execute("DELETE FROM produtos WHERE id = ?", (dup_id,))
        produtos_removidos += 1
        print(f"    [REMOVE_PRODUTO] id={dup_id}")

# =========================
# 3. FINALIZAR
# =========================
conn.commit()

# sanity check: preços órfãos
cur.execute("""
    SELECT COUNT(*)
    FROM precos p
    LEFT JOIN produtos pr ON pr.id = p.produto_id
    WHERE pr.id IS NULL
""")
precos_orfaos = cur.fetchone()[0]

conn.close()

print("\n========== RESUMO DEDUP ==========")
print("Grupos processados:", grupos_processados)
print("Produtos removidos:", produtos_removidos)
print("Preços movidos:", precos_movidos)
print("Preços descartados por duplicidade:", precos_descartados)
print("Preços órfãos:", precos_orfaos)
print("==================================")
