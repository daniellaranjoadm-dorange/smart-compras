import requests
import json

url = "https://www.atacadao.com.br/api/catalog_system/pub/products/search?fq=C:312"

headers = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0"
}

resp = requests.get(url, headers=headers, timeout=30)

print("STATUS:", resp.status_code)

try:
    data = resp.json()
    print("TOTAL PRODUTOS:", len(data))

    if data:
        print("\n=== PRODUTO 0 ===")
        print(json.dumps(data[0], ensure_ascii=False, indent=2)[:4000])

    with open("atacadao_produtos.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("\nOK: salvo em atacadao_produtos.json")

except Exception as e:
    print("ERRO:", e)
    print(resp.text[:1000])
