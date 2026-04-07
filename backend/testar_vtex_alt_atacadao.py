import requests
import json

tests = [
    "https://www.atacadao.com.br/api/catalog_system/pub/products/search?ft=arroz",
    "https://www.atacadao.com.br/api/catalog_system/pub/products/search?fq=C:/bebidas/cervejas",
    "https://www.atacadao.com.br/api/catalog_system/pub/products/search?fq=C:/mercearia/biscoitos",
    "https://www.atacadao.com.br/api/catalog_system/pub/products/search?fq=C:312&_from=0&_to=9",
    "https://www.atacadao.com.br/api/catalog_system/pub/products/search?_from=0&_to=9&ft=arroz",
    "https://www.atacadao.com.br/api/catalog_system/pub/products/search?_from=0&_to=9&fq=C:/catalogo",
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
        try:
            data = r.json()
            if isinstance(data, list):
                print("TOTAL:", len(data))
                if data and isinstance(data[0], dict):
                    print("CHAVES_ITEM_0:", list(data[0].keys())[:30])
                    print(json.dumps(data[0], ensure_ascii=False, indent=2)[:1500])
            else:
                print("TIPO:", type(data).__name__)
                print(json.dumps(data, ensure_ascii=False, indent=2)[:1500])
        except Exception:
            print("BODY:", r.text[:1000])
    except Exception as e:
        print("ERRO:", repr(e))
