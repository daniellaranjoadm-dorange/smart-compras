import json
import requests

url = "https://h0zdqmtdm8yw09jqm82tknt0g4.c360a.salesforce.com/web/v2/authentication"

print("Cole o Request Payload da chamada /web/v2/authentication")
print("Exemplo: client_id=...&siteId=...&...")

payload = input("PAYLOAD: ").strip()

headers = {
    "Accept": "*/*",
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "https://www.atacadao.com.br",
    "Referer": "https://www.atacadao.com.br/loja/rio-grande",
    "User-Agent": "Mozilla/5.0",
}

resp = requests.post(url, headers=headers, data=payload, timeout=30)

print("STATUS:", resp.status_code)
print("CONTENT-TYPE:", resp.headers.get("content-type"))
print("SET-COOKIE:", resp.headers.get("set-cookie"))

try:
    data = resp.json()
    print("JSON:")
    print(json.dumps(data, ensure_ascii=False, indent=2)[:4000])

    with open("atacadao_auth_response.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("OK: salvo em atacadao_auth_response.json")
except Exception:
    print("BODY_RAW:")
    print(resp.text[:4000])
