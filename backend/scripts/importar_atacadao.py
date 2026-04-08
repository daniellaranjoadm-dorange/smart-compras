import sys
import io

# FORÇA UTF-8 NO PYTHON (resolve acentuação no log)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


# VERSÃO LIMPA COM CONTROLE DE TRANSAÇÃO CORRETO

import sys
from pathlib import Path
from decimal import Decimal
import requests
import time

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from app.db.base import SessionLocal
from app.models.entities import Produto, PrecoProduto, UnidadeMercado
from app.services.normalizacao_produto import gerar_assinatura_produto

ATACADAO_UNIDADE_NOME = "Atacadao Rio Grande"
SEARCH_URL = "https://www.atacadao.com.br/api/io/_v/api/intelligent-search/product_search"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
}

TERMOS = ["arroz", "feijao", "cafe"]

def get_or_create_unidade(db):
    unidade = db.query(UnidadeMercado).filter_by(nome=ATACADAO_UNIDADE_NOME).first()
    if unidade:
        return unidade

    unidade = UnidadeMercado(nome=ATACADAO_UNIDADE_NOME)
    db.add(unidade)
    db.flush()
    return unidade

def extrair_nome(p):
    return p.get("productName") or p.get("name")

def extrair_preco(p):
    try:
        items = p.get("items") or []
        for item in items:
            for seller in item.get("sellers", []):
                offer = seller.get("commertialOffer", {})
                preco = offer.get("Price")
                if preco:
                    return Decimal(str(preco))
    except:
        pass
    return None

def buscar(termo, page):
    r = requests.get(SEARCH_URL, headers=HEADERS, params={
        "query": termo,
        "page": page,
        "count": 50
    }, timeout=30)
    r.raise_for_status()
    data = r.json()

    if isinstance(data, list):
        return data

    for k in ["products", "records", "items"]:
        if isinstance(data.get(k), list):
            return data[k]

    return []

def get_or_create_produto(db, nome, assinatura):
    p = db.query(Produto).filter_by(assinatura=assinatura).first()
    if p:
        return p, False

    p = Produto(nome=nome, assinatura=assinatura)
    db.add(p)
    db.flush()
    return p, True

def upsert_preco(db, produto_id, unidade_id, preco):
    db.flush()

    existente = db.query(PrecoProduto).filter_by(
        produto_id=produto_id,
        unidade_id=unidade_id
    ).first()

    if existente:
        existente.preco = preco
        return

    try:
        db.add(PrecoProduto(
            produto_id=produto_id,
            unidade_id=unidade_id,
            preco=preco
        ))
        db.flush()
    except:
        db.rollback()
        existente = db.query(PrecoProduto).filter_by(
            produto_id=produto_id,
            unidade_id=unidade_id
        ).first()
        if existente:
            existente.preco = preco

def main():
    db = SessionLocal()
    unidade = get_or_create_unidade(db)

    try:
        for termo in TERMOS:
            print(f"\n=== {termo.upper()} ===")

            for page in range(1, 4):
                produtos = buscar(termo, page)

                for p in produtos:
                    nome = extrair_nome(p)
                    preco = extrair_preco(p)

                    if not nome or not preco:
                        continue

                    assinatura = gerar_assinatura_produto(nome)
                    if not assinatura or not assinatura.startswith(termo):
                        continue

                    produto, _ = get_or_create_produto(db, nome, assinatura)
                    upsert_preco(db, produto.id, unidade.id, preco)

                    print(f"[OK] {nome} | {preco}")

                db.commit()
                time.sleep(0.5)

    finally:
        db.commit()
        db.close()

if __name__ == "__main__":
    main()
