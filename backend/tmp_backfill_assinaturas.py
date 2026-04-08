# -*- coding: utf-8 -*-
import requests
from app.services.normalizacao_produto import gerar_assinatura_produto

BACKEND_URL = "http://127.0.0.1:8011"

resp = requests.get(f"{BACKEND_URL}/api/produtos", timeout=60)
resp.raise_for_status()
produtos = resp.json()

total = 0
atualizados = 0
sem_assinatura = 0

for p in produtos:
    total += 1
    produto_id = p["id"]
    nome = p["nome"]
    assinatura_atual = p.get("assinatura")
    assinatura_nova = gerar_assinatura_produto(nome)

    if not assinatura_nova:
        sem_assinatura += 1
        continue

    if assinatura_atual == assinatura_nova:
        continue

    payload = {
        "nome": nome,
        "categoria_id": p.get("categoria_id"),
        "assinatura": assinatura_nova
    }

    # tentativa de update por PUT, se existir
    put_ok = False
    try:
        r = requests.put(f"{BACKEND_URL}/api/produtos/{produto_id}", json=payload, timeout=30)
        if r.status_code in (200, 201):
            put_ok = True
    except Exception:
        pass

    if put_ok:
        atualizados += 1
        print(f"[BACKFILL_OK] id={produto_id} assinatura={assinatura_nova}")
        continue

    print(f"[BACKFILL_SKIP] id={produto_id} sem rota PUT /api/produtos/{{id}}")

print("========== RESUMO BACKFILL ==========")
print("Produtos lidos:", total)
print("Produtos atualizados:", atualizados)
print("Produtos sem assinatura geravel:", sem_assinatura)
print("=====================================")
