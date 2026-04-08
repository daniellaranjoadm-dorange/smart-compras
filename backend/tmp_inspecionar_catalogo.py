# -*- coding: utf-8 -*-
import requests
import re
import unicodedata
from collections import defaultdict

BACKEND_URL = "http://127.0.0.1:8011"

def normalize_text(value: str) -> str:
    value = value or ""
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value

resp = requests.get(f"{BACKEND_URL}/api/produtos", timeout=60)
resp.raise_for_status()
produtos = resp.json()

grupos = defaultdict(list)

for p in produtos:
    nome = p.get("nome", "")
    base = normalize_text(nome)

    if "arroz" in base:
        grupos["arroz"].append(nome)
    if "feijao" in base:
        grupos["feijao"].append(nome)
    if "papel higienico" in base:
        grupos["papel_higienico"].append(nome)
    if "cafe" in base:
        grupos["cafe"].append(nome)
    if "leite" in base:
        grupos["leite"].append(nome)

for chave, itens in grupos.items():
    print(f"\n=== {chave.upper()} ({len(itens)}) ===")
    for nome in sorted(set(itens))[:60]:
        print(nome)
