import re
import unicodedata

from app.db.base import SessionLocal
from app.models.entities import Produto

STOPWORDS = {
    "tipo", "de", "da", "do", "e", "com", "sem", "para", "tradicional",
    "premium", "refinado", "agulhinha", "branco"
}

def normalizar(texto):
    if not texto:
        return ""
    texto = texto.lower().strip()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"[^a-z0-9\s\.\,\-]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def extrair_medida(nome):
    nome_norm = normalizar(nome).replace(",", ".")

    padroes = [
        r"(\d+(?:\.\d+)?)\s*(kg)",
        r"(\d+(?:\.\d+)?)\s*(g)",
        r"(\d+(?:\.\d+)?)\s*(l)",
        r"(\d+(?:\.\d+)?)\s*(ml)",
    ]

    for padrao in padroes:
        m = re.search(padrao, nome_norm)
        if m:
            valor = float(m.group(1))
            unidade = m.group(2)

            if unidade == "kg":
                return valor * 1000, "g"
            if unidade == "l":
                return valor * 1000, "ml"
            return valor, unidade

    return None, None


def remover_medida(texto):
    texto = re.sub(r"\d+(?:[\.\,]\d+)?\s*(kg|g|l|ml)\b", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def tokenizar_base(nome):
    nome = normalizar(nome)
    nome = remover_medida(nome)
    tokens = nome.split()

    tokens_limpos = []
    for t in tokens:
        if t in STOPWORDS:
            continue
        if re.fullmatch(r"\d+", t):
            continue
        tokens_limpos.append(t)

    return tokens_limpos


def assinatura_produto(nome):
    tokens = tokenizar_base(nome)
    medida_valor, medida_unidade = extrair_medida(nome)

    assinatura_base = " ".join(tokens[:5]).strip()

    if medida_valor is not None and medida_unidade:
        medida_txt = f"{int(medida_valor) if medida_valor == int(medida_valor) else medida_valor}{medida_unidade}"
    else:
        medida_txt = "sem_medida"

    assinatura = f"{assinatura_base} | {medida_txt}"
    return assinatura_base, medida_valor, medida_unidade, assinatura


def run():
    db = SessionLocal()
    produtos = db.query(Produto).order_by(Produto.nome.asc()).all()

    print()
    print("===== AUDITORIA DE NORMALIZACAO =====")
    print(f"TOTAL PRODUTOS NO BANCO: {len(produtos)}")
    print()

    grupos = {}

    for produto in produtos:
        base, medida_valor, medida_unidade, assinatura = assinatura_produto(produto.nome)

        if assinatura not in grupos:
            grupos[assinatura] = []

        grupos[assinatura].append({
            "id": produto.id,
            "nome": produto.nome,
            "base": base,
            "medida_valor": medida_valor,
            "medida_unidade": medida_unidade,
        })

    for assinatura, itens in grupos.items():
        print("=" * 100)
        print("ASSINATURA:", assinatura)
        print("QTD ITENS:", len(itens))
        for item in itens:
            print(f"[{item['id']}] {item['nome']}")

    print()
    print("===== RESUMO =====")
    print("TOTAL ASSINATURAS:", len(grupos))

    db.close()


if __name__ == "__main__":
    run()
