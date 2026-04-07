import json
from pathlib import Path

import requests
from dotenv import dotenv_values

env = {str(k).lstrip("\ufeff"): v for k, v in dotenv_values(".env.stok").items()}

AUTH = env.get("STOK_AUTH_BEARER", "").strip()
SESSAO = env.get("STOK_SESSAO_ID", "").strip()
ORG = env.get("STOK_ORGANIZATION_ID", "130").strip()
DOMAIN = env.get("STOK_DOMAIN_KEY", "stokonline.com.br").strip()

resultados = json.loads(Path("stok_vitrines_resultado.json").read_text(encoding="utf-8"))

vitrine_ok = None
for row in resultados:
    vitrine, status, total_items = row
    if status == 200 and isinstance(total_items, int) and total_items > 0:
        vitrine_ok = vitrine
        break

if not vitrine_ok:
    print("ERRO: nenhuma vitrine com produtos encontrada")
    raise SystemExit(1)

print("VITRINE_OK:", vitrine_ok)

headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {AUTH}",
    "Content-Type": "application/json",
    "domainKey": DOMAIN,
    "organizationid": ORG,
    "Origin": "https://www.stokonline.com.br",
    "Referer": "https://www.stokonline.com.br/",
    "sessao-id": SESSAO,
    "User-Agent": "Mozilla/5.0",
}

url = f"https://services.vipcommerce.com.br/api-admin/v1/org/130/filial/1/centro_distribuicao/2/loja/vitrines/produtos?vitrine_ids={vitrine_ok}&page=1&limit=10"
resp = requests.get(url, headers=headers, timeout=30)
data = resp.json()

Path("stok_primeira_vitrine_com_produtos.json").write_text(
    json.dumps(data, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print("STATUS:", resp.status_code)
print("OK: salvo em stok_primeira_vitrine_com_produtos.json")
