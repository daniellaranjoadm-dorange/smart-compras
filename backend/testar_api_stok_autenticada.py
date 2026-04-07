import json
import os
from pathlib import Path

import requests
from dotenv import dotenv_values

env = {str(k).lstrip("\ufeff"): v for k, v in dotenv_values(".env.stok").items()}

AUTH = env.get("STOK_AUTH_BEARER", "").strip()
SESSAO = env.get("STOK_SESSAO_ID", "").strip()
ORG = env.get("STOK_ORGANIZATION_ID", "130").strip()
DOMAIN = env.get("STOK_DOMAIN_KEY", "stokonline.com.br").strip()

if not AUTH or not SESSAO:
    print("ERRO: preencha STOK_AUTH_BEARER e STOK_SESSAO_ID no .env.stok")
    raise SystemExit(1)

url = "https://services.vipcommerce.com.br/api-admin/v1/org/130/filial/1/centro_distribuicao/2/loja/vitrines/produtos?vitrine_ids=1d9ee708-8f08-11f0-b67d-fa163ec2ffea&page=1&limit=10"

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

resp = requests.get(url, headers=headers, timeout=30)

print("STATUS:", resp.status_code)
print("CONTENT-TYPE:", resp.headers.get("content-type"))

try:
    data = resp.json()
except Exception:
    print("BODY_RAW:", resp.text[:2000])
    raise SystemExit(1)

if isinstance(data, dict):
    print("CHAVES_TOPO:", list(data.keys())[:30])

Path("stok_api_auth_sample.json").write_text(
    json.dumps(data, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print("OK: resposta salva em stok_api_auth_sample.json")
