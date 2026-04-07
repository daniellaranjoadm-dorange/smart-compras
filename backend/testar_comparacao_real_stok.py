import requests

LISTA_ID = 3  # <-- TROCAR PELO ID IMPRESSO
CIDADE_ID = 6   # Rio Grande, ajuste se necessário
from pathlib import Path

token_file = Path(".smart_token")
if token_file.exists():
    TOKEN = token_file.read_text(encoding="utf-8").lstrip("\ufeff").strip()
else:
    TOKEN = input("Cole o smartcompras_token: ").strip()

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
    print(r.text[:3000])
