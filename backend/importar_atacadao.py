# importar_atacadao.py
# -*- coding: utf-8 -*-

import re
import sys
import time
import logging
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, Iterable, Optional, Tuple

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from sqlalchemy.exc import IntegrityError
from unidecode import unidecode

from app.db.base import SessionLocal
from app.models.entities import Produto, UnidadeMercado, PrecoProduto


ATACADAO_BASE = "https://www.atacadao.com.br"
ATACADAO_SEARCH_URL = (
    "https://www.atacadao.com.br/api/io/_v/api/intelligent-search/"
    "product_search/trade-policy/1"
)

STORE_NAME = "Atacadao Rio Grande"
STORE_CITY = "Rio Grande"
STORE_UF = "RS"

SEARCH_TERMS = [
    "arroz",
    "feijao",
    "acucar",
    "cafe",
    "oleo",
    "macarrao",
    "farinha",
    "sal",
    "leite",
    "manteiga",
    "margarina",
    "molho de tomate",
    "extrato de tomate",
    "sabao em po",
    "detergente",
    "papel higienico",
    "cerveja",
    "refrigerante",
    "agua mineral",
]

PAGE_SIZE = 50
MAX_PAGES_PER_TERM = 10
REQUEST_TIMEOUT = 30
SLEEP_BETWEEN_REQUESTS = 0.4

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("importar_atacadao")


def build_session() -> requests.Session:
    session = requests.Session()

    retries = Retry(
        total=5,
        connect=5,
        read=5,
        backoff_factor=1.0,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    session.headers.update({
        "Accept": "application/json",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Referer": f"{ATACADAO_BASE}/loja/rio-grande",
        "Origin": ATACADAO_BASE,
    })
    return session


def normalize_text(value: Optional[str]) -> str:
    if not value:
        return ""
    value = unidecode(value).lower().strip()
    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"[^a-z0-9\s]", " ", value)
    value = re.sub(r"\s+", " ", value).strip()

    stopwords = {
        "tipo", "pct", "pacote", "embalagem", "com", "de", "da", "do", "e",
        "o", "a"
    }
    tokens = [t for t in value.split() if t not in stopwords]
    return " ".join(tokens)


def extract_category(categories: Any) -> Optional[str]:
    if isinstance(categories, list) and categories:
        return categories[0].strip("/") or None
    return None


def extract_ean(product: Dict[str, Any]) -> Optional[str]:
    items = product.get("items") or []
    for item in items:
        ean = item.get("ean")
        if ean:
            return str(ean).strip()
    return None


def extract_price(product: Dict[str, Any]) -> Optional[Decimal]:
    try:
        low = (
            product.get("priceRange", {})
            .get("sellingPrice", {})
            .get("lowPrice")
        )
        if low is not None:
            return Decimal(str(low))
    except (InvalidOperation, TypeError, ValueError):
        pass

    items = product.get("items") or []
    for item in items:
        for seller in item.get("sellers") or []:
            offer = seller.get("commertialOffer") or {}
            price = offer.get("Price")
            if price is not None:
                try:
                    return Decimal(str(price))
                except (InvalidOperation, TypeError, ValueError):
                    continue

    return None


def build_source_id(product: Dict[str, Any]) -> str:
    product_id = str(product.get("productId") or "").strip()
    if product_id:
        return product_id

    items = product.get("items") or []
    if items:
        item_id = str(items[0].get("itemId") or "").strip()
        if item_id:
            return item_id

    return ""


def build_product_url(product: Dict[str, Any]) -> Optional[str]:
    link = product.get("link")
    if not link:
        return None
    if link.startswith("http://") or link.startswith("https://"):
        return link
    return f"{ATACADAO_BASE}{link}"


def get_model_columns(model) -> set[str]:
    return {c.name for c in model.__table__.columns}


PRODUTO_COLS = get_model_columns(Produto)
UNIDADE_COLS = get_model_columns(UnidadeMercado)
PRECO_COLS = get_model_columns(PrecoProduto)


def pick_first(existing: set[str], *names: str) -> Optional[str]:
    for name in names:
        if name in existing:
            return name
    return None


UNIDADE_NOME_COL = pick_first(UNIDADE_COLS, "nome", "nome_unidade", "descricao")
UNIDADE_CIDADE_COL = pick_first(UNIDADE_COLS, "cidade")
UNIDADE_UF_COL = pick_first(UNIDADE_COLS, "uf", "estado")

PRODUTO_NOME_COL = pick_first(PRODUTO_COLS, "nome", "nome_produto", "descricao")
PRODUTO_EAN_COL = pick_first(PRODUTO_COLS, "ean", "codigo_barras")
PRODUTO_MARCA_COL = pick_first(PRODUTO_COLS, "marca")
PRODUTO_CATEGORIA_COL = pick_first(PRODUTO_COLS, "categoria")
PRODUTO_DESC_COL = pick_first(PRODUTO_COLS, "descricao", "descricao_produto")
PRODUTO_NORM_COL = pick_first(PRODUTO_COLS, "nome_normalizado")

PRECO_VALOR_COL = pick_first(PRECO_COLS, "preco", "valor", "preco_unitario")
PRECO_PRODUTO_ID_COL = pick_first(PRECO_COLS, "produto_id")
PRECO_UNIDADE_ID_COL = pick_first(PRECO_COLS, "unidade_id", "unidade_mercado_id")
PRECO_FONTE_COL = pick_first(PRECO_COLS, "fonte")
PRECO_FONTE_ID_COL = pick_first(PRECO_COLS, "fonte_id")
PRECO_URL_COL = pick_first(PRECO_COLS, "url_origem", "url")


def model_to_dict(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


def get_or_create_unidade(db):
    if not UNIDADE_NOME_COL:
        raise RuntimeError(f"Nao achei coluna de nome em UnidadeMercado: {sorted(UNIDADE_COLS)}")

    unidade = db.query(UnidadeMercado).filter(
        getattr(UnidadeMercado, UNIDADE_NOME_COL) == STORE_NAME
    ).first()

    if unidade:
        return unidade

    # pega qualquer unidade existente pra copiar rede_id e cidade_id
    base = db.query(UnidadeMercado).first()
    if not base:
        raise RuntimeError("Nenhuma unidade existente encontrada para herdar rede_id")

    data = {
        UNIDADE_NOME_COL: STORE_NAME,
        "rede_id": base.rede_id,
        "cidade_id": base.cidade_id,
    }

    unidade = UnidadeMercado(**data)
    db.add(unidade)
    db.commit()
    db.refresh(unidade)
    logger.info("Unidade criada: %s (rede_id=%s)", STORE_NAME, base.rede_id)
    return unidade

    data = {UNIDADE_NOME_COL: STORE_NAME}
    if UNIDADE_CIDADE_COL:
        data[UNIDADE_CIDADE_COL] = STORE_CITY
    if UNIDADE_UF_COL:
        data[UNIDADE_UF_COL] = STORE_UF

    unidade = UnidadeMercado(**data)
    db.add(unidade)
    db.commit()
    db.refresh(unidade)
    logger.info("Unidade criada: %s", STORE_NAME)
    return unidade


def find_existing_product(db, nome: str, ean: Optional[str], nome_normalizado: str):
    if PRODUTO_EAN_COL and ean:
        produto = db.query(Produto).filter(
            getattr(Produto, PRODUTO_EAN_COL) == ean
        ).first()
        if produto:
            return produto

    if PRODUTO_NOME_COL:
        produto = db.query(Produto).filter(
            getattr(Produto, PRODUTO_NOME_COL) == nome
        ).first()
        if produto:
            return produto

    if PRODUTO_NORM_COL:
        produto = db.query(Produto).filter(
            getattr(Produto, PRODUTO_NORM_COL) == nome_normalizado
        ).first()
        if produto:
            return produto

    return None


def create_or_update_product(db, raw_product: Dict[str, Any]) -> Tuple[Any, bool]:
    nome = (raw_product.get("productName") or "").strip()
    if not nome:
        raise ValueError("Produto sem productName")

    if not PRODUTO_NOME_COL:
        raise RuntimeError(f"Nao achei coluna de nome em Produto: {sorted(PRODUTO_COLS)}")

    ean = extract_ean(raw_product)
    marca = raw_product.get("brand")
    categoria = extract_category(raw_product.get("categories"))
    descricao = raw_product.get("description")
    nome_normalizado = normalize_text(nome)

    produto = find_existing_product(db, nome, ean, nome_normalizado)
    created = False

    if produto is None:
        data = {PRODUTO_NOME_COL: nome}

        if PRODUTO_NORM_COL:
            data[PRODUTO_NORM_COL] = nome_normalizado
        if PRODUTO_EAN_COL:
            data[PRODUTO_EAN_COL] = ean
        if PRODUTO_MARCA_COL:
            data[PRODUTO_MARCA_COL] = marca
        if PRODUTO_CATEGORIA_COL:
            data[PRODUTO_CATEGORIA_COL] = categoria
        if PRODUTO_DESC_COL:
            data[PRODUTO_DESC_COL] = descricao

        produto = Produto(**data)
        db.add(produto)
        db.commit()
        db.refresh(produto)
        created = True
        return produto, created

    changed = False

    if PRODUTO_EAN_COL and not getattr(produto, PRODUTO_EAN_COL, None) and ean:
        setattr(produto, PRODUTO_EAN_COL, ean)
        changed = True
    if PRODUTO_MARCA_COL and not getattr(produto, PRODUTO_MARCA_COL, None) and marca:
        setattr(produto, PRODUTO_MARCA_COL, marca)
        changed = True
    if PRODUTO_CATEGORIA_COL and not getattr(produto, PRODUTO_CATEGORIA_COL, None) and categoria:
        setattr(produto, PRODUTO_CATEGORIA_COL, categoria)
        changed = True
    if PRODUTO_DESC_COL and not getattr(produto, PRODUTO_DESC_COL, None) and descricao:
        setattr(produto, PRODUTO_DESC_COL, descricao)
        changed = True
    if PRODUTO_NORM_COL and not getattr(produto, PRODUTO_NORM_COL, None):
        setattr(produto, PRODUTO_NORM_COL, nome_normalizado)
        changed = True

    if changed:
        db.commit()
        db.refresh(produto)

    return produto, created


def upsert_price(db, produto, unidade, preco_valor: Decimal, raw_product: Dict[str, Any]) -> Tuple[Any, bool]:
    if not PRECO_PRODUTO_ID_COL or not PRECO_UNIDADE_ID_COL or not PRECO_VALOR_COL:
        raise RuntimeError(
            f"Colunas obrigatorias de PrecoProduto nao encontradas: {sorted(PRECO_COLS)}"
        )

    existing = db.query(PrecoProduto).filter(
        getattr(PrecoProduto, PRECO_PRODUTO_ID_COL) == produto.id,
        getattr(PrecoProduto, PRECO_UNIDADE_ID_COL) == unidade.id,
    ).first()

    url_origem = build_product_url(raw_product)
    fonte_id = build_source_id(raw_product)

    if existing:
        changed = False

        if Decimal(str(getattr(existing, PRECO_VALOR_COL))) != preco_valor:
            setattr(existing, PRECO_VALOR_COL, preco_valor)
            changed = True

        if PRECO_FONTE_COL and getattr(existing, PRECO_FONTE_COL, None) != "atacadao":
            setattr(existing, PRECO_FONTE_COL, "atacadao")
            changed = True

        if PRECO_FONTE_ID_COL and getattr(existing, PRECO_FONTE_ID_COL, None) != fonte_id:
            setattr(existing, PRECO_FONTE_ID_COL, fonte_id)
            changed = True

        if PRECO_URL_COL and getattr(existing, PRECO_URL_COL, None) != url_origem:
            setattr(existing, PRECO_URL_COL, url_origem)
            changed = True

        if changed:
            db.commit()
            db.refresh(existing)

        return existing, False

    data = {
        PRECO_PRODUTO_ID_COL: produto.id,
        PRECO_UNIDADE_ID_COL: unidade.id,
        PRECO_VALOR_COL: preco_valor,
    }
    if PRECO_FONTE_COL:
        data[PRECO_FONTE_COL] = "atacadao"
    if PRECO_FONTE_ID_COL:
        data[PRECO_FONTE_ID_COL] = fonte_id
    if PRECO_URL_COL:
        data[PRECO_URL_COL] = url_origem

    novo = PrecoProduto(**data)
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo, True


def fetch_products_by_query(session: requests.Session, query: str, page: int, count: int = PAGE_SIZE):
    params = {
        "query": query,
        "page": page,
        "count": count,
    }

    resp = session.get(
        ATACADAO_SEARCH_URL,
        params=params,
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()

    data = resp.json()
    products = data.get("products", [])
    if not isinstance(products, list):
        return []
    return products


def iter_all_products(session: requests.Session) -> Iterable[Dict[str, Any]]:
    seen_ids = set()

    for term in SEARCH_TERMS:
        logger.info("Buscando termo: %s", term)

        for page in range(1, MAX_PAGES_PER_TERM + 1):
            try:
                products = fetch_products_by_query(session, term, page, PAGE_SIZE)
            except Exception as e:
                logger.exception("Erro buscando termo=%s page=%s: %s", term, page, e)
                break

            if not products:
                logger.info("Sem resultados para termo=%s page=%s", term, page)
                break

            logger.info("Recebidos %s produtos para termo=%s page=%s", len(products), term, page)

            added_this_page = 0

            for product in products:
                source_id = build_source_id(product)
                dedupe_key = source_id or f"{term}:{product.get('productName', '')}"
                if dedupe_key in seen_ids:
                    continue
                seen_ids.add(dedupe_key)
                added_this_page += 1
                yield product

            if len(products) < PAGE_SIZE:
                break

            if added_this_page == 0:
                break

            time.sleep(SLEEP_BETWEEN_REQUESTS)


def process_product(db, unidade, raw_product: Dict[str, Any]) -> Tuple[bool, bool, bool]:
    nome = (raw_product.get("productName") or "").strip()
    preco = extract_price(raw_product)

    if not nome:
        logger.warning("Produto ignorado: sem nome")
        return False, False, False

    if preco is None:
        logger.warning("Produto ignorado sem preco: %s", nome)
        return False, False, False

    try:
        produto, produto_criado = create_or_update_product(db, raw_product)
        _, preco_criado = upsert_price(db, produto, unidade, preco, raw_product)
        return produto_criado, preco_criado, True
    except IntegrityError:
        db.rollback()
        logger.exception("IntegrityError processando produto: %s", nome)
        return False, False, False
    except Exception:
        db.rollback()
        logger.exception("Erro processando produto: %s", nome)
        return False, False, False


def main() -> int:
    logger.info("Iniciando importer do Atacadao")
    logger.info("Loja alvo: %s", STORE_NAME)
    logger.info("Produto cols: %s", sorted(PRODUTO_COLS))
    logger.info("Unidade cols: %s", sorted(UNIDADE_COLS))
    logger.info("Preco cols: %s", sorted(PRECO_COLS))

    http = build_session()
    db = SessionLocal()

    total_lidos = 0
    total_processados = 0
    total_produtos_criados = 0
    total_precos_criados = 0

    try:
        unidade = get_or_create_unidade(db)

        for raw_product in iter_all_products(http):
            total_lidos += 1

            produto_criado, preco_criado, processado = process_product(db, unidade, raw_product)
            if processado:
                total_processados += 1
            if produto_criado:
                total_produtos_criados += 1
            if preco_criado:
                total_precos_criados += 1

            if total_lidos % 25 == 0:
                logger.info(
                    "Parcial | lidos=%s processados=%s produtos_novos=%s precos_novos=%s",
                    total_lidos,
                    total_processados,
                    total_produtos_criados,
                    total_precos_criados,
                )

        logger.info("FINALIZADO")
        logger.info("Total lidos: %s", total_lidos)
        logger.info("Total processados: %s", total_processados)
        logger.info("Produtos criados: %s", total_produtos_criados)
        logger.info("Precos criados: %s", total_precos_criados)
        return 0

    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
