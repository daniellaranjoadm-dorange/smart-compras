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

palavras = ["product", "produto", "card", "item", "price", "preco", "valor"]

for nome, url in sites.items():
    print(f"\n===== {nome.upper()} =====")
    try:
        r = requests.get(url, headers=headers, timeout=25)
        soup = BeautifulSoup(r.text, "html.parser")

        candidatos = []
        for tag in soup.find_all(True):
            classes = " ".join(tag.get("class", []))
            ident = tag.get("id", "")
            texto = f"{tag.name} {classes} {ident}".lower()
            if any(p in texto for p in palavras):
                candidatos.append(tag)

        print("CANDIDATOS_ENCONTRADOS:", len(candidatos))
        vistos = 0
        for tag in candidatos[:15]:
            print("\nTAG:", tag.name)
            print("CLASS:", tag.get("class"))
            print("ID:", tag.get("id"))
            print("HTML:", str(tag)[:500].replace("\n", " "))
            vistos += 1

        if vistos == 0:
            print("Nenhum card óbvio encontrado no HTML inicial.")

    except Exception as e:
        print("ERRO:", repr(e))
