import requests
import json

URL = "https://www.atacadao.com.br/api/io/_v/api/intelligent-search/product_search"

params = {
    "query": "arroz",
    "page": 1,
    "count": 10
}

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

resp = requests.get(URL, params=params, headers=headers, timeout=30)

print("STATUS:", resp.status_code)
print("URL FINAL:", resp.url)
print()

try:
    data = resp.json()
except Exception:
    print("Resposta nao veio em JSON")
    print(resp.text[:2000])
    raise

print("TIPO DO JSON:", type(data).__name__)
print("CHAVES PRINCIPAIS:", list(data.keys())[:20] if isinstance(data, dict) else "nao e dict")
print()

if isinstance(data, dict):
    produtos = data.get("products") or data.get("records") or data.get("items") or []
elif isinstance(data, list):
    produtos = data
else:
    produtos = []

print("TOTAL PRODUTOS ENCONTRADOS:", len(produtos))
print()

for i, item in enumerate(produtos[:10], start=1):
    nome = item.get("productName") or item.get("name") or "SEM NOME"

    preco = None

    price_range = item.get("priceRange", {})
    if isinstance(price_range, dict):
        selling = price_range.get("sellingPrice", {})
        if isinstance(selling, dict):
            preco = selling.get("lowPrice")

    if preco is None:
        sellers = item.get("sellers", [])
        if sellers and isinstance(sellers, list):
            offer = sellers[0].get("commertialOffer", {})
            if isinstance(offer, dict):
                preco = offer.get("Price")

    print(f"{i}. {nome} | PRECO: {preco}")
