import requests
from bs4 import BeautifulSoup

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

for nome, url in sites.items():
    print(f"\n===== {nome.upper()} =====")
    try:
        r = requests.get(url, headers=headers, timeout=25)
        print("URL:", url)
        print("STATUS:", r.status_code)
        print("CONTENT-TYPE:", r.headers.get("content-type"))
        print("TAMANHO_HTML:", len(r.text))

        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.title.get_text(" ", strip=True) if soup.title else "(sem title)"
        print("TITLE:", title)

        textos_preco = soup.find_all(string=lambda s: s and "R$" in s)
        print("TEXTOS_COM_PRECO:", len(textos_preco))
        for t in textos_preco[:10]:
            print(" -", t.strip()[:120])

        scripts = soup.find_all("script")
        print("QTD_SCRIPTS:", len(scripts))

        body_text = soup.get_text(" ", strip=True)
        print("AMOSTRA_BODY:", body_text[:300])

    except Exception as e:
        print("ERRO:", repr(e))
