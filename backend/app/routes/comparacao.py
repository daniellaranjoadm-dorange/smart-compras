from app.services.normalizacao_produto import gerar_assinatura_produto
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



def dados_assinatura_do_produto(produto):
    def montar(assinatura: str | None):
        if not assinatura:
            return None

        # formato novo: cafe_250g / feijao_carioca_1kg
        if "_" in assinatura and " | " not in assinatura:
            partes = assinatura.split("_")
            base = partes[0] if partes else None

            medida_valor = None
            medida_unidade = None

            for token in reversed(partes):
                m = re.match(r"^(\d+(?:\.\d+)?)(kg|g|ml|l|m|rolos)$", token)
                if m:
                    try:
                        medida_valor = float(m.group(1))
                    except Exception:
                        medida_valor = None
                    medida_unidade = m.group(2)
                    break

            return assinatura, base, medida_valor, medida_unidade

        # formato legado: "base | 5g"
        if " | " in assinatura:
            partes = assinatura.split(" | ", 1)
            base = partes[0].strip()
            medida_txt = partes[1].strip() if len(partes) > 1 else ""

            medida_valor = None
            medida_unidade = None

            m = re.match(r"^(\d+(?:\.\d+)?)(kg|g|ml|l|m|rolos)$", medida_txt)
            if m:
                try:
                    medida_valor = float(m.group(1))
                except Exception:
                    medida_valor = None
                medida_unidade = m.group(2)

            return assinatura, base, medida_valor, medida_unidade

        return None

    # PRIORIDADE TOTAL: core novo
    assinatura_nova = gerar_assinatura_produto(produto.nome)
    dados = montar(assinatura_nova)
    if dados:
        return dados

    # se o core novo disser que nao serve, ignora produto
    return None, None, None, None


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




def score_relevancia_comparacao(base: str, medida_valor, medida_unidade) -> float:
    if medida_valor is None or not medida_unidade:
        return 0.0

    alvo = None

    if base == "cafe":
        if medida_unidade == "g":
            alvo = 500
        elif medida_unidade == "kg":
            alvo = 0.5
    elif base == "feijao":
        if medida_unidade == "g":
            alvo = 1000
        elif medida_unidade == "kg":
            alvo = 1
    elif base == "arroz":
        if medida_unidade == "g":
            alvo = 5000
        elif medida_unidade == "kg":
            alvo = 5
    elif base == "leite":
        if medida_unidade == "ml":
            alvo = 1000
        elif medida_unidade == "l":
            alvo = 1

    if alvo is None:
        return 1.0

    return 100000.0 - abs(float(medida_valor) - float(alvo))


@router.get("")
def comparar_produtos(
    q: str = Query(..., min_length=2),
    categoria: str | None = Query(default=None),
    limit_produtos: int = Query(default=150, le=400),
    db: Session = Depends(get_db),
):
    q_norm = normalizar(q).strip()
    tokens_q = tokens_relevantes_query(q)

    consulta = db.query(Produto, Categoria).outerjoin(Categoria, Produto.categoria_id == Categoria.id)

    if categoria:
        consulta = consulta.filter(Categoria.nome == categoria)

    produtos_encontrados = consulta.order_by(Produto.nome.asc()).limit(5000).all()

    grupos = {}

    for produto, categoria_obj in produtos_encontrados:
        if produto_bloqueado(produto.nome):
            continue

        assinatura, base, medida_valor, medida_unidade = dados_assinatura_do_produto(produto)

        if not assinatura or not base:
            continue

        # BLOQUEIO PRODUTOS SEM MEDIDA (CRÍTICO)
        if medida_valor is None or not medida_unidade:
            continue

        # BLOQUEIO ASSINATURA LIXO
        if assinatura.endswith("_na"):
            continue

        base_norm = normalizar(base).strip()

        # matching semântico exato por base
        if base_norm != q_norm:
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
            -score_relevancia_comparacao(
                g.get("base"),
                g.get("medida_valor"),
                g.get("medida_unidade"),
            ),
            g["menor_preco"] if g["menor_preco"] is not None else 999999,
            g["assinatura"]
        )
    )

    return {
        "q": q,
        "tokens_q": tokens_q,
        "total_grupos": len(grupos_ordenados),
        "grupos": grupos_ordenados[:limit_produtos]
    }
