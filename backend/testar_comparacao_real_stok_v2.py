import requests
from pathlib import Path

LISTA_ID = 4
CIDADE_ID = 5

TOKEN = Path(".smart_token").read_text(encoding="utf-8").lstrip("\ufeff").strip()

base = "http://127.0.0.1:8010/api"

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

urls = [
    f"{base}/comparacao/cidade/{CIDADE_ID}/lista/{LISTA_ID}",
    f"{base}/comparacao/cidade/{CIDADE_ID}/lista/{LISTA_ID}/otimizada",
    f"{base}/resumo/cidade/{CIDADE_ID}/lista/{LISTA_ID}",
]

for url in urls:
    print("\n===", url, "===")
    r = requests.get(url, headers=headers, timeout=30)
    print("STATUS:", r.status_code)
    print(r.text[:4000])
