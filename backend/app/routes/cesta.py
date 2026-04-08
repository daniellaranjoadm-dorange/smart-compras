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

router = APIRouter(prefix="/api/catalogo/cesta", tags=["cesta"])

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

REGRAS_ITEM = {
    "arroz": {
        "bloquear": {"macarrao", "instantaneo", "refresco", "sem acucar", "vinagre", "mucilon", "biscoito"},
        "medida_min": 500
    },
    "feijao": {
        "bloquear": {"caldo", "sopa", "feijoada", "tempero"},
        "medida_min": 500
    },
    "acucar": {
        "bloquear": {"sem acucar", "zero", "adocante", "refresco", "clight", "gelatina"},
        "medida_min": 500
    }
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
    assinatura_salva = getattr(produto, "assinatura", None)

    def montar(assinatura: str | None):
        if not assinatura:
            return None

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

    dados = montar(assinatura_salva)
    if dados:
        return dados

    assinatura_nova = gerar_assinatura_produto(produto.nome)
    dados = montar(assinatura_nova)
    if dados:
        return dados

    return assinatura_produto(produto.nome)


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




def score_relevancia_item(base: str, medida_valor, medida_unidade) -> float:
    if medida_valor is None or not medida_unidade:
        return 0.0

    alvo = None

    if base == "cafe":
        if medida_unidade == "g":
            alvo = 500
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
    elif base == "acucar":
        if medida_unidade == "g":
            alvo = 1000
        elif medida_unidade == "kg":
            alvo = 1
    elif base == "oleo":
        if medida_unidade == "ml":
            alvo = 900
        elif medida_unidade == "l":
            alvo = 0.9

    if alvo is None:
        return 1.0

    return 100000.0 - abs(float(medida_valor) - float(alvo))


def produto_valido_para_item(termo: str, nome_produto: str, medida_valor):
    termo_norm = normalizar(termo)
    nome_norm = normalizar(nome_produto)

    regra = REGRAS_ITEM.get(termo_norm)
    if not regra:
        return True

    for bloqueado in regra["bloquear"]:
        if bloqueado in nome_norm:
            return False

    medida_min = regra["medida_min"]
    if medida_valor is None or medida_valor < medida_min:
        return False

    return True


def ofertas_para_item(db: Session, termo: str, categoria: str | None):
    termo_norm = normalizar(termo).strip()

    consulta = db.query(Produto, Categoria).outerjoin(Categoria, Produto.categoria_id == Categoria.id)

    if categoria:
        consulta = consulta.filter(Categoria.nome == categoria)

    produtos_encontrados = consulta.order_by(Produto.nome.asc()).limit(5000).all()

    ofertas = []

    for produto, categoria_obj in produtos_encontrados:
        if produto_bloqueado(produto.nome):
            continue

        assinatura, base, medida_valor, medida_unidade = dados_assinatura_do_produto(produto)

        if not assinatura or not base:
            continue

        base_norm = normalizar(base).strip()

        # matching semântico exato por base
        if base_norm != termo_norm:
            continue

        if medida_valor is None or not medida_unidade:
            continue

        precos_raw = (
            db.query(PrecoProduto, UnidadeMercado, RedeMercado, Cidade)
            .join(UnidadeMercado, PrecoProduto.unidade_id == UnidadeMercado.id)
            .join(RedeMercado, UnidadeMercado.rede_id == RedeMercado.id)
            .join(Cidade, UnidadeMercado.cidade_id == Cidade.id)
            .filter(PrecoProduto.produto_id == produto.id)
            .all()
        )

        for preco, unidade, rede, cidade in precos_raw:
            valor = float(preco.preco)
            if valor <= 0:
                continue

            ofertas.append({
                "query_item": termo,
                "assinatura": assinatura,
                "base": base,
                "medida_valor": medida_valor,
                "medida_unidade": medida_unidade,
                "categoria": categoria_obj.nome if categoria_obj else None,
                "produto_id": produto.id,
                "produto_nome": produto.nome,
                "preco": valor,
                "unidade_id": unidade.id,
                "unidade_nome": unidade.nome,
                "rede": rede.nome,
                "cidade": cidade.nome
            })

    ofertas = sorted(
        ofertas,
        key=lambda x: (
            -score_relevancia_item(
                x.get("base"),
                x.get("medida_valor"),
                x.get("medida_unidade"),
            ),
            x["preco"],
        )
    )

    return ofertas


@router.get("")
def calcular_cesta(
    itens: str = Query(..., description="Lista separada por virgula. Ex: arroz,feijao,acucar"),
    categoria: str | None = Query(default="mercearia"),
    db: Session = Depends(get_db),
):
    lista_itens = [x.strip() for x in itens.split(",") if x.strip()]

    encontrados = []
    nao_encontrados = []
    total_melhor_por_item = 0.0
    ofertas_por_item = {}

    for item in lista_itens:
        ofertas = ofertas_para_item(db, item, categoria)

        if not ofertas:
            nao_encontrados.append(item)
            continue

        melhor = ofertas[0]
        encontrados.append(melhor)
        ofertas_por_item[item] = ofertas
        total_melhor_por_item += melhor["preco"]

    encontrados = sorted(encontrados, key=lambda x: x["preco"])

    totais_por_unidade = {}

    for item in lista_itens:
        ofertas = ofertas_por_item.get(item, [])
        for oferta in ofertas:
            chave = str(oferta["unidade_id"])

            if chave not in totais_por_unidade:
                totais_por_unidade[chave] = {
                    "unidade_id": oferta["unidade_id"],
                    "unidade_nome": oferta["unidade_nome"],
                    "rede": oferta["rede"],
                    "cidade": oferta["cidade"],
                    "itens": {},
                    "total": 0.0
                }

            atual = totais_por_unidade[chave]["itens"].get(item)

            if atual is None:
                totais_por_unidade[chave]["itens"][item] = oferta
            else:
                score_atual = score_relevancia_item(
                    atual.get("base"),
                    atual.get("medida_valor"),
                    atual.get("medida_unidade"),
                )
                score_novo = score_relevancia_item(
                    oferta.get("base"),
                    oferta.get("medida_valor"),
                    oferta.get("medida_unidade"),
                )

                if (
                    score_novo > score_atual or
                    (score_novo == score_atual and oferta["preco"] < atual["preco"])
                ):
                    totais_por_unidade[chave]["itens"][item] = oferta

    mercados_analisados = []

    for unidade in totais_por_unidade.values():
        itens_cobertos = list(unidade["itens"].keys())
        total = sum(x["preco"] for x in unidade["itens"].values())

        unidade["itens_cobertos"] = itens_cobertos
        unidade["total_itens_cobertos"] = len(itens_cobertos)
        unidade["total"] = round(total, 2)
        unidade["faltando"] = [x for x in lista_itens if x not in itens_cobertos]

        mercados_analisados.append(unidade)

    mercados_analisados = sorted(
        mercados_analisados,
        key=lambda x: (-x["total_itens_cobertos"], x["total"])
    )

    melhor_mercado = mercados_analisados[0] if mercados_analisados else None

    economia_absoluta = None
    economia_percentual = None

    if melhor_mercado and melhor_mercado["total_itens_cobertos"] == len(encontrados):
        economia_absoluta = round(melhor_mercado["total"] - round(total_melhor_por_item, 2), 2)
        if melhor_mercado["total"] > 0:
            economia_percentual = round((economia_absoluta / melhor_mercado["total"]) * 100, 2)

    return {
        "categoria": categoria,
        "itens_solicitados": lista_itens,
        "itens_encontrados": encontrados,
        "itens_nao_encontrados": nao_encontrados,
        "total_itens_encontrados": len(encontrados),
        "total_itens_nao_encontrados": len(nao_encontrados),
        "total_cesta_melhor_por_item": round(total_melhor_por_item, 2),
        "melhor_mercado_cesta": melhor_mercado,
        "economia_absoluta": economia_absoluta,
        "economia_percentual": economia_percentual,
        "mercados_analisados": mercados_analisados[:10]
    }
