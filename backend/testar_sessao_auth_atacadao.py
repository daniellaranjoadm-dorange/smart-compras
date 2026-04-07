import requests
import json

s = requests.Session()

auth_url = "https://h0zdqmtdm8yw09jqm82tknt0g4.c360a.salesforce.com/web/v2/authentication"
payload = "auth=eyJhcHBTb3VyY2VJZCI6IjJmNjZhYjM3LTMwNDQtNGI5Mi04MGQ4LWFiNjVjNTEzNGViMCIsImRldmljZUlkIjoiNTY3Y2I2YjQyMzM2YTBhNyJ9"

auth_headers = {
    "Accept": "*/*",
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "https://www.atacadao.com.br",
    "Referer": "https://www.atacadao.com.br/loja/rio-grande",
    "User-Agent": "Mozilla/5.0",
}

auth_resp = s.post(auth_url, headers=auth_headers, data=payload, timeout=30)
print("AUTH STATUS:", auth_resp.status_code)

jwt = auth_resp.json().get("jwt", "")
print("JWT OK:", bool(jwt))

tests = [
    "https://www.atacadao.com.br/api/catalog_system/pub/products/search?_from=0&_to=9&ft=arroz",
    "https://www.atacadao.com.br/api/io/_v/api/intelligent-search/product_search/trade-policy/1?query=arroz&page=1&count=10",
]

headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {jwt}",
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.atacadao.com.br/loja/rio-grande",
    "Origin": "https://www.atacadao.com.br",
}

for url in tests:
    print("\n===", url, "===")
    r = s.get(url, headers=headers, timeout=30)
    print("STATUS:", r.status_code)
    print(r.text[:2000])
