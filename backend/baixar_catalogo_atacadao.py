import requests
import json

url = "https://www.atacadao.com.br/_next/data/kbkxERXOOdtEafFqfHwEM/pt-BR/catalogo.json?slug=catalogo"

headers = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.atacadao.com.br/loja/rio-grande",
}

resp = requests.get(url, headers=headers, timeout=30)

print("STATUS:", resp.status_code)
print("CONTENT-TYPE:", resp.headers.get("content-type"))

data = resp.json()

with open("atacadao_catalogo.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("OK: salvo em atacadao_catalogo.json")
print("CHAVES_TOPO:", list(data.keys())[:30])
print(json.dumps(data, ensure_ascii=False, indent=2)[:4000])
