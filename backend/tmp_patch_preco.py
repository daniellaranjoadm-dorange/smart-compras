# -*- coding: utf-8 -*-
import re

path = r".\scripts\importar_atacadao.py"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old_extract = r'''def extract_price(product: dict):
    direct_candidates = [
        product.get("price"),
        product.get("sellingPrice"),
        product.get("Price"),
        product.get("spotPrice"),
        product.get("bestPrice"),
    ]

    for c in direct_candidates:
        val = to_decimal(c)
        if val is not None:
            return val

    items = product.get("items") or []
    for item in items:
        sellers = item.get("sellers") or []
        for seller in sellers:
            offer = seller.get("commertialOffer") or seller.get("commercialOffer") or {}
            for c in (
                offer.get("Price"),
                offer.get("price"),
                offer.get("ListPrice"),
                offer.get("listPrice"),
                offer.get("spotPrice"),
            ):
                val = to_decimal(c)
                if val is not None:
                    return val

    return None
'''

new_extract = r'''def extract_price(product: dict):
    candidates = [
        product.get("price"),
        product.get("sellingPrice"),
        product.get("Price"),
        product.get("spotPrice"),
        product.get("bestPrice"),
        product.get("listPrice"),
        product.get("ListPrice"),
    ]

    for c in candidates:
        val = to_decimal(c)
        if val is not None and val > 0:
            return val

    items = product.get("items") or []
    for item in items:
        item_candidates = [
            item.get("price"),
            item.get("sellingPrice"),
            item.get("Price"),
            item.get("spotPrice"),
            item.get("bestPrice"),
            item.get("listPrice"),
            item.get("ListPrice"),
        ]
        for c in item_candidates:
            val = to_decimal(c)
            if val is not None and val > 0:
                return val

        sellers = item.get("sellers") or []
        for seller in sellers:
            offer = seller.get("commertialOffer") or seller.get("commercialOffer") or {}
            nested_candidates = [
                offer.get("Price"),
                offer.get("price"),
                offer.get("ListPrice"),
                offer.get("listPrice"),
                offer.get("spotPrice"),
                offer.get("spotPriceInPercent"),
                offer.get("sellingPrice"),
            ]
            for c in nested_candidates:
                val = to_decimal(c)
                if val is not None and val > 0:
                    return val

    price_def = product.get("priceDefinition") or {}
    for c in (
        price_def.get("sellingPrice"),
        price_def.get("calculatedSellingPrice"),
        price_def.get("total"),
        price_def.get("value"),
    ):
        val = to_decimal(c)
        if val is not None and val > 0:
            return val

    return None
'''

if old_extract not in content:
    raise SystemExit("Bloco extract_price nao encontrado exatamente como esperado.")

content = content.replace(old_extract, new_extract)

content = content.replace(
    "                if not name or price is None:\n                    continue",
    "                if not name or price is None or price <= 0:\n                    continue"
)

with open(path, "w", encoding="utf-8", newline="\n") as f:
    f.write(content)

print("PATCH_OK")
