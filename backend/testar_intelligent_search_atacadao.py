import requests

tests = [
    "https://www.atacadao.com.br/api/io/_v/api/intelligent-search/product_search/trade-policy/1?query=arroz&page=1&count=10",
    "https://www.atacadao.com.br/api/io/_v/api/intelligent-search/product_search/trade-policy/1?query=cerveja&page=1&count=10",
    "https://www.atacadao.com.br/api/io/_v/api/intelligent-search/facets?query=arroz",
]

headers = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.atacadao.com.br/loja/rio-grande",
}

for url in tests:
    print("\n===", url, "===")
    try:
        r = requests.get(url, headers=headers, timeout=30)
        print("STATUS:", r.status_code)
        print("CONTENT-TYPE:", r.headers.get("content-type"))
        print(r.text[:2000])
    except Exception as e:
        print("ERRO:", repr(e))
