import requests
from pathlib import Path

TOKEN = Path(".smart_token").read_text(encoding="utf-8").lstrip("\ufeff").strip()
base = "http://127.0.0.1:8010/api"

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

r = requests.get(f"{base}/cidades", headers=headers, timeout=30)
print("STATUS:", r.status_code)
print(r.text[:4000])
