from pathlib import Path
import requests

sites = {
    "atacadao": "https://www.atacadao.com.br/loja/rio-grande",
    "stok": "https://www.stokonline.com.br/",
    "krolow": "https://macroatacadokrolow.com.br/",
    "gbmix": "https://gbmixonline.com.br/",
    "ecomix": "https://ecomixatacarejo.com.br/",
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}

out = Path("tmp_html_mercados")
out.mkdir(exist_ok=True)

for nome, url in sites.items():
    try:
        r = requests.get(url, headers=headers, timeout=25)
        path = out / f"{nome}.html"
        path.write_text(r.text, encoding="utf-8", errors="ignore")
        print("OK:", path)
    except Exception as e:
        print("ERRO:", nome, repr(e))
