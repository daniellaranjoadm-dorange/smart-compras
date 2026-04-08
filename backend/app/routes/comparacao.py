import re
import unicodedata

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entities import (
    Produto,
    Categoria,
    PrecoProduto,
    UnidadeMercado,
    RedeMercado,
    Cidade,
)

router = APIRouter(prefix="/api/catalogo/comparar", tags=["comparacao"])

STOPWORDS = {
    "tipo", "de", "da", "do", "e", "com", "sem", "para",
    "tradicional", "premium", "refinado", "agulhinha", "branco"
}

TERMOS_BLOQUEADOS_GERAIS = {
    "cao", "caes", "cachorro", "pet", "baw waw",
    "lubrificante", "motor", "desengripante",
    "swift"
}

TERMOS_BLOQUEADOS_COMIDA_PRONTA = {
    "pronto", "cremoso", "carreteiro", "congelado"
}


def normalizar(texto: str) -> str:
    texto = (texto or "").lower().strip()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"[^a-z0-9\s\.\,\-]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def extrair_medida(nome: str):
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


def remover_medida(texto: str) -> str:
    texto = re.sub(r"\d+(?:[\.\,]\d+)?\s*(kg|g|l|ml)\b", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def assinatura_produto(nome: str):
    nome_norm = normalizar(nome)
    nome_sem_medida = remover_medida(nome_norm)

    tokens = []
    for token in nome_sem_medida.split():
        if token in STOPWORDS:
            continue
        if re.fullmatch(r"\d+", token):
            continue
        tokens.append(token)

    base = " ".join(tokens[:5]).strip()
    medida_valor, medida_unidade = extrair_medida(nome)

    if medida_valor is not None and medida_unidade:
        medida_txt = f"{int(medida_valor) if medida_valor == int(medida_valor) else medida_valor}{medida_unidade}"
    else:
        medida_txt = "sem_medida"

    assinatura = f"{base} | {medida_txt}"
    return assinatura, base, medida_valor, medida_unidade


def produto_bloqueado(nome: str) -> bool:
    nome_norm = normalizar(nome)

    for termo in TERMOS_BLOQUEADOS_GERAIS:
        if termo in nome_norm:
            return True

    for termo in TERMOS_BLOQUEADOS_COMIDA_PRONTA:
        if termo in nome_norm:
            return True

    return False


def tokens_relevantes_query(q: str):
    q_norm = normalizar(q)
    tokens = []
    for t in q_norm.split():
        if len(t) < 2:
            continue
        if t in STOPWORDS:
            continue
        tokens.append(t)
    return tokens


@router.get("")
def comparar_produtos(
    q: str = Query(..., min_length=2),
    categoria: str | None = Query(default=None),
    limit_produtos: int = Query(default=150, le=400),
    db: Session = Depends(get_db),
):
    tokens_q = tokens_relevantes_query(q)

    consulta = (
        db.query(Produto, Categoria)
        .outerjoin(Categoria, Produto.categoria_id == Categoria.id)
        .filter(Produto.nome.ilike(f"%{q}%"))
    )

    if categoria:
        consulta = consulta.filter(Categoria.nome == categoria)

    produtos_encontrados = consulta.order_by(Produto.nome.asc()).limit(limit_produtos).all()

    if not produtos_encontrados:
        return {
            "q": q,
            "tokens_q": tokens_q,
            "total_grupos": 0,
            "grupos": []
        }

    grupos = {}

    for produto, categoria_obj in produtos_encontrados:
        nome_norm = normalizar(produto.nome)

        if produto_bloqueado(produto.nome):
            continue

        if tokens_q and not all(token in nome_norm for token in tokens_q):
            continue

        assinatura, base, medida_valor, medida_unidade = assinatura_produto(produto.nome)

        if medida_valor is None:
            continue

        precos_raw = (
            db.query(PrecoProduto, UnidadeMercado, RedeMercado, Cidade)
            .join(UnidadeMercado, PrecoProduto.unidade_id == UnidadeMercado.id)
            .join(RedeMercado, UnidadeMercado.rede_id == RedeMercado.id)
            .join(Cidade, UnidadeMercado.cidade_id == Cidade.id)
            .filter(PrecoProduto.produto_id == produto.id)
            .all()
        )

        precos_validos = []
        for preco, unidade, rede, cidade in precos_raw:
            valor = float(preco.preco)
            if valor <= 0:
                continue

            precos_validos.append({
                "preco_id": preco.id,
                "preco": valor,
                "unidade_id": unidade.id,
                "unidade_nome": unidade.nome,
                "rede": rede.nome,
                "cidade": cidade.nome
            })

        if not precos_validos:
            continue

        precos_validos = sorted(precos_validos, key=lambda x: x["preco"])
        melhor_oferta_produto = precos_validos[0]

        if assinatura not in grupos:
            grupos[assinatura] = {
                "assinatura": assinatura,
                "base": base,
                "medida_valor": medida_valor,
                "medida_unidade": medida_unidade,
                "categoria": categoria_obj.nome if categoria_obj else None,
                "produtos": [],
                "menor_preco": None,
                "melhor_oferta": None,
                "total_ofertas": 0
            }

        grupos[assinatura]["produtos"].append({
            "produto_id": produto.id,
            "nome": produto.nome,
            "precos": precos_validos
        })

        grupos[assinatura]["total_ofertas"] += len(precos_validos)

        menor_atual = grupos[assinatura]["menor_preco"]
        if menor_atual is None or melhor_oferta_produto["preco"] < menor_atual:
            grupos[assinatura]["menor_preco"] = melhor_oferta_produto["preco"]
            grupos[assinatura]["melhor_oferta"] = melhor_oferta_produto

    grupos_ordenados = sorted(
        grupos.values(),
        key=lambda g: (
            g["menor_preco"] if g["menor_preco"] is not None else 999999,
            g["assinatura"]
        )
    )

    return {
        "q": q,
        "tokens_q": tokens_q,
        "total_grupos": len(grupos_ordenados),
        "grupos": grupos_ordenados
    }
