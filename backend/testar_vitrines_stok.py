import json
from pathlib import Path
from urllib.parse import urlparse, parse_qs

import requests
from dotenv import dotenv_values

env = {str(k).lstrip("\ufeff"): v for k, v in dotenv_values(".env.stok").items()}

AUTH = env.get("STOK_AUTH_BEARER", "").strip()
SESSAO = env.get("STOK_SESSAO_ID", "").strip()
ORG = env.get("STOK_ORGANIZATION_ID", "130").strip()
DOMAIN = env.get("STOK_DOMAIN_KEY", "stokonline.com.br").strip()

if not AUTH or not SESSAO:
    print("ERRO: .env.stok incompleto")
    raise SystemExit(1)

url_base = "https://services.vipcommerce.com.br/api-admin/v1/org/130/filial/1/centro_distribuicao/2/loja/vitrines/produtos?vitrine_ids=63c2b626-2782-11f1-bd2f-fa163ec2ffea,caaeff3a-278b-11f1-bd2f-fa163ec2ffea,aee9b205-26e3-11f1-bd2f-fa163ec2ffea,a907ed9c-26e4-11f1-bd2f-fa163ec2ffea,abd0a154-26e9-11f1-bd2f-fa163ec2ffea,fc486912-27b2-11f1-bd2f-fa163ec2ffea,6762902e-27b6-11f1-bd2f-fa163ec2ffea,9e031f3c-2d3c-11f1-acb0-fa163ec2ffea,b2c1897b-2d3c-11f1-acb0-fa163ec2ffea,baf67adc-2d3d-11f1-acb0-fa163ec2ffea,d2aa1b2f-2d3d-11f1-acb0-fa163ec2ffea,1373f889-2d3e-11f1-acb0-fa163ec2ffea,2b36d16a-2d3e-11f1-acb0-fa163ec2ffea,3d442da9-2d3e-11f1-acb0-fa163ec2ffea,52f63a2d-2d3e-11f1-acb0-fa163ec2ffea,61c3de80-2d3e-11f1-acb0-fa163ec2ffea,7607dad7-2d3e-11f1-acb0-fa163ec2ffea,890f9c0e-2d3e-11f1-acb0-fa163ec2ffea,9c6cd6a8-2d3e-11f1-acb0-fa163ec2ffea,b2c3ad51-2d3e-11f1-acb0-fa163ec2ffea,c49cd054-2d3e-11f1-acb0-fa163ec2ffea,d4ed5cd5-2d3e-11f1-acb0-fa163ec2ffea,f0563756-2d3e-11f1-acb0-fa163ec2ffea,06b6187e-2d3f-11f1-acb0-fa163ec2ffea,133d8fd0-2d3f-11f1-acb0-fa163ec2ffea,45f5dc4e-2d41-11f1-acb0-fa163ec2ffea,58cd8619-2d41-11f1-acb0-fa163ec2ffea,da987f43-2e89-11f1-acb0-fa163ec2ffea,2f6421da-2e8a-11f1-acb0-fa163ec2ffea,c4421e55-2e95-11f1-acb0-fa163ec2ffea,e5546514-2e95-11f1-acb0-fa163ec2ffea,fcc3d2b6-2e95-11f1-acb0-fa163ec2ffea,1183b647-2e96-11f1-acb0-fa163ec2ffea,938d6340-2e96-11f1-acb0-fa163ec2ffea,d881af13-2e96-11f1-acb0-fa163ec2ffea,ea1945ee-2e96-11f1-acb0-fa163ec2ffea,07a460cc-2e97-11f1-acb0-fa163ec2ffea,196d31a9-2e97-11f1-acb0-fa163ec2ffea,2887c9fb-2e97-11f1-acb0-fa163ec2ffea,38900376-2e97-11f1-acb0-fa163ec2ffea,45d9b602-2e97-11f1-acb0-fa163ec2ffea,552ee051-2e97-11f1-acb0-fa163ec2ffea,731e1cd0-2e97-11f1-acb0-fa163ec2ffea,838de8a0-2e97-11f1-acb0-fa163ec2ffea,c8f5e8b4-2e97-11f1-acb0-fa163ec2ffea,d9c90156-2e97-11f1-acb0-fa163ec2ffea,00eb4c78-2e98-11f1-acb0-fa163ec2ffea,0df9bf31-2e98-11f1-acb0-fa163ec2ffea,201e4b3f-2e98-11f1-acb0-fa163ec2ffea,52ed381d-2e99-11f1-acb0-fa163ec2ffea&page=1&limit=10"

qs = parse_qs(urlparse(url_base).query)
vitrines = qs.get("vitrine_ids", [""])[0].split(",")

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

resultados = []

for vitrine in vitrines:
    url = f"https://services.vipcommerce.com.br/api-admin/v1/org/130/filial/1/centro_distribuicao/2/loja/vitrines/produtos?vitrine_ids={vitrine}&page=1&limit=10"
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        data = resp.json()
        total_items = 0
        if isinstance(data, dict):
            paginator = data.get("paginator") or {}
            total_items = paginator.get("total_items", 0) or 0
        resultados.append((vitrine, resp.status_code, total_items))
        print(f"{vitrine} | status={resp.status_code} | total_items={total_items}")
    except Exception as e:
        resultados.append((vitrine, "ERRO", repr(e)))
        print(f"{vitrine} | ERRO={repr(e)}")

Path("stok_vitrines_resultado.json").write_text(
    json.dumps(resultados, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print("OK: resultado salvo em stok_vitrines_resultado.json")
