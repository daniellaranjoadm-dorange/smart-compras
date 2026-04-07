import requests
from pathlib import Path

TOKEN = Path(".smart_token").read_text(encoding="utf-8").lstrip("\ufeff").strip()
base = "http://127.0.0.1:8010/api"

LISTA_ID = 4  # <-- TROCAR PELO ID RETORNADO NO PASSO ANTERIOR

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

itens = [
    {"lista_id": LISTA_ID, "produto_id": 11, "quantidade": 1},
    {"lista_id": LISTA_ID, "produto_id": 24, "quantidade": 1},
    {"lista_id": LISTA_ID, "produto_id": 15, "quantidade": 1},
]

for item in itens:
    r = requests.post(f"{base}/itens", headers=headers, json=item, timeout=30)
    print("\nITEM:", item)
    print("STATUS:", r.status_code)
    print(r.text[:2000])
