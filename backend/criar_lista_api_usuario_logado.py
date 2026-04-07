import requests
from pathlib import Path

TOKEN = Path(".smart_token").read_text(encoding="utf-8").lstrip("\ufeff").strip()
base = "http://127.0.0.1:8010/api"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

payload = {
    "nome": "Lista real Stok Rio Grande API"
}

r = requests.post(f"{base}/listas", headers=headers, json=payload, timeout=30)

print("STATUS:", r.status_code)
print(r.text)
