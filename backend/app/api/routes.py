from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import true
import csv
import io

from app.db.base import Base, engine
from app.db.session import get_db
from app.core.security import criar_access_token, decodificar_access_token, gerar_hash_senha, verificar_senha
from app.core.deps import get_current_user
from app.models.entities import (
    Categoria,
    Cidade,
    Estado,
    HistoricoPreco,
    ItemListaCompra,
    ItemListaModelo,
    ListaCompra,
    ListaModelo,
    PrecoProduto,
    Produto,
    RedeMercado,
    UnidadeMercado,
    Usuario)
from app.schemas.entities import (
    CategoriaCreate,
    CategoriaRead,
    CidadeCreate,
    CidadeRead,
    LoginRequest,
    TokenResponse,
    ComparacaoCidadeOtimizadaResponse,
    ComparacaoCidadeResponse,
    EstadoCreate,
    EstadoRead,
    HistoricoPrecoRead,
    ItemListaCompraCreate,
    ItemListaCompraRead,
    ItemListaModeloCreate,
    ItemListaModeloRead,
    ListaCompraCreate,
    ListaCompraRead,
    ListaModeloCreate,
    ListaModeloRead,
    PrecoProdutoCreate,
    PrecoProdutoRead,
    ProdutoCreate,
    ProdutoRead,
    RedeMercadoCreate,
    RedeMercadoRead,
    ResumoInteligenteResponse,
    UnidadeMercadoCreate,
    UnidadeMercadoRead,
    UsuarioCreate,
    UsuarioRead)
from app.services.comparacao_local import (
    comparar_lista_otimizada_por_cidade,
    comparar_lista_por_cidade,
    gerar_resumo_inteligente_compra)

Base.metadata.create_all(bind=engine)

router = APIRouter()


@router.post("/usuarios", response_model=UsuarioRead)
def criar_usuario(payload: UsuarioCreate, db: Session = Depends(get_db)):
    dados = payload.model_dump()
    senha = dados.pop("senha", None)

    item = Usuario(**dados)
    if senha:
        item.senha_hash = gerar_hash_senha(senha)

    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email ja cadastrado.")
    db.refresh(item)
    return item


@router.get("/usuarios", response_model=list[UsuarioRead])
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(Usuario).order_by(Usuario.nome).all()


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == payload.email).first()

    if not usuario or not usuario.senha_hash:
        raise HTTPException(status_code=401, detail="Credenciais invalidas.")

    if not verificar_senha(payload.senha, usuario.senha_hash):
        raise HTTPException(status_code=401, detail="Credenciais invalidas.")

    token = criar_access_token({
        "sub": str(usuario.id),
        "email": usuario.email,
        "nome": usuario.nome,
    })

    return {"access_token": token, "token_type": "bearer"}


@router.post("/estados", response_model=EstadoRead)
def criar_estado(payload: EstadoCreate, db: Session = Depends(get_db)):
    item = Estado(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/estados", response_model=list[EstadoRead])
def listar_estados(db: Session = Depends(get_db)):
    return db.query(Estado).order_by(Estado.nome).all()


@router.post("/cidades", response_model=CidadeRead)
def criar_cidade(payload: CidadeCreate, db: Session = Depends(get_db)):
    item = Cidade(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/cidades", response_model=list[CidadeRead])
def listar_cidades(db: Session = Depends(get_db)):
    return db.query(Cidade).order_by(Cidade.nome).all()


@router.get("/cidades/estado/{estado_id}", response_model=list[CidadeRead])
def listar_cidades_por_estado(estado_id: int, db: Session = Depends(get_db)):
    return db.query(Cidade).filter(Cidade.estado_id == estado_id).order_by(Cidade.nome).all()


@router.post("/redes-mercado", response_model=RedeMercadoRead)
def criar_rede(payload: RedeMercadoCreate, db: Session = Depends(get_db)):
    item = RedeMercado(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/redes-mercado", response_model=list[RedeMercadoRead])
def listar_redes(db: Session = Depends(get_db)):
    return db.query(RedeMercado).order_by(RedeMercado.nome).all()


@router.post("/unidades-mercado", response_model=UnidadeMercadoRead)
def criar_unidade(payload: UnidadeMercadoCreate, db: Session = Depends(get_db)):
    item = UnidadeMercado(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/unidades-mercado", response_model=list[UnidadeMercadoRead])
def listar_unidades(db: Session = Depends(get_db)):
    return db.query(UnidadeMercado).order_by(UnidadeMercado.nome).all()


@router.get("/unidades-mercado/cidade/{cidade_id}", response_model=list[UnidadeMercadoRead])
def listar_unidades_por_cidade(cidade_id: int, db: Session = Depends(get_db)):
    return db.query(UnidadeMercado).filter(UnidadeMercado.cidade_id == cidade_id).order_by(UnidadeMercado.nome).all()


@router.post("/categorias", response_model=CategoriaRead)
def criar_categoria(payload: CategoriaCreate, db: Session = Depends(get_db)):
    item = Categoria(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/categorias", response_model=list[CategoriaRead])
def listar_categorias(db: Session = Depends(get_db)):
    return db.query(Categoria).order_by(Categoria.nome).all()


@router.post("/produtos", response_model=ProdutoRead)
def criar_produto(payload: ProdutoCreate, db: Session = Depends(get_db)):
    item = Produto(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/produtos", response_model=list[ProdutoRead])
def listar_produtos(db: Session = Depends(get_db)):
    return db.query(Produto).order_by(Produto.nome).all()


@router.post("/listas-modelo", response_model=ListaModeloRead)
def criar_lista_modelo(payload: ListaModeloCreate, db: Session = Depends(get_db)):
    item = ListaModelo(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/listas-modelo", response_model=list[ListaModeloRead])
def listar_listas_modelo(
    db: Session = Depends(get_db)):
    return db.query(ListaModelo).filter(
        ListaModelo.usuario_id == usuario.id
    ).order_by(ListaModelo.nome).all()


@router.post("/itens-lista-modelo", response_model=ItemListaModeloRead)
def criar_item_lista_modelo(
    payload: ItemListaModeloCreate,
    db: Session = Depends(get_db)):
    lista_modelo = db.query(ListaModelo).filter(
        ListaModelo.id == payload.lista_modelo_id,
        ListaModelo.usuario_id == usuario.id
    ).first()

    if not lista_modelo:
        raise HTTPException(status_code=404, detail="Lista modelo nao encontrada.")

    item = ItemListaModelo(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/itens-lista-modelo", response_model=list[ItemListaModeloRead])
def listar_itens_lista_modelo(
    db: Session = Depends(get_db),

    lista_modelo_id: int | None = None
):
    query = db.query(ItemListaModelo).join(
    ListaModelo, ItemListaModelo.lista_modelo_id == ListaModelo.id
).filter(
    ListaModelo.usuario_id == usuario.id
)
    if lista_modelo_id is not None:
        query = query.filter(ItemListaModelo.lista_modelo_id == lista_modelo_id)
    return query.all()


@router.post("/listas", response_model=ListaCompraRead)
def criar_lista(
    payload: dict,
    db: Session = Depends(get_db)
):
    nome = payload.get("nome")
    if not nome:
        raise HTTPException(status_code=400, detail="Campo nome e obrigatorio.")

    usuario_id = payload.get("usuario_id") or 1

    item = ListaCompra(
        nome=nome,
        usuario_id=usuario_id
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.get("/listas", response_model=list[ListaCompraRead])
def listar_listas(
    db: Session = Depends(get_db)
):
    return db.query(ListaCompra).order_by(ListaCompra.nome).all()

@router.post("/listas-modelo/{lista_modelo_id}/gerar", response_model=ListaCompraRead)
def gerar_lista_de_modelo(
    lista_modelo_id: int,
    db: Session = Depends(get_db)):
    modelo = db.query(ListaModelo).filter(
    ListaModelo.id == lista_modelo_id,
    ListaModelo.usuario_id == usuario.id
).first()
    if not modelo:
        raise HTTPException(status_code=404, detail="Lista modelo nao encontrada.")

    agora = datetime.now()
    nome_lista = f"{modelo.nome} - {agora.strftime('%Y-%m-%d')}"

    nova_lista = ListaCompra(
        usuario_id=modelo.usuario_id,
        nome=nome_lista,
        gerada_de_modelo_id=modelo.id,
        gerada_em=agora)
    db.add(nova_lista)
    db.commit()
    db.refresh(nova_lista)

    itens_modelo = db.query(ItemListaModelo).filter(ItemListaModelo.lista_modelo_id == modelo.id).all()

    for item in itens_modelo:
        novo_item = ItemListaCompra(
            lista_id=nova_lista.id,
            produto_id=item.produto_id,
            quantidade=item.quantidade)
        db.add(novo_item)

    db.commit()
    db.refresh(nova_lista)
    return nova_lista


@router.post("/itens", response_model=ItemListaCompraRead)
def criar_item(
    payload: ItemListaCompraCreate,
    db: Session = Depends(get_db)
):
    lista = db.query(ListaCompra).filter(
        ListaCompra.id == payload.lista_id
    ).first()

    if not lista:
        raise HTTPException(status_code=404, detail="Lista nao encontrada")

    item = ItemListaCompra(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.get("/itens", response_model=list[ItemListaCompraRead])
def listar_itens(
    db: Session = Depends(get_db)
):
    return db.query(ItemListaCompra).all()

@router.post("/precos", response_model=PrecoProdutoRead)
def criar_preco(payload: PrecoProdutoCreate, db: Session = Depends(get_db)):
    existente = db.query(PrecoProduto).filter(
        PrecoProduto.produto_id == payload.produto_id,
        PrecoProduto.unidade_id == payload.unidade_id).first()

    historico = HistoricoPreco(
        produto_id=payload.produto_id,
        unidade_id=payload.unidade_id,
        preco=payload.preco)
    db.add(historico)

    if existente:
        existente.preco = payload.preco
        db.commit()
        db.refresh(existente)
        return existente

    item = PrecoProduto(**payload.model_dump())
    db.add(item)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Nao foi possivel salvar o preco.")

    db.refresh(item)
    return item


@router.post("/precos/importar-csv")
def importar_precos_csv(arquivo: UploadFile = File(...), db: Session = Depends(get_db)):
    if not arquivo.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Envie um arquivo CSV.")

    conteudo = arquivo.file.read().decode("utf-8-sig")
    leitor = csv.DictReader(io.StringIO(conteudo))

    obrigatorias = {"produto_id", "unidade_id", "preco"}
    if not leitor.fieldnames or not obrigatorias.issubset(set(leitor.fieldnames)):
        raise HTTPException(status_code=400, detail="CSV invalido. Colunas obrigatorias: produto_id, unidade_id, preco.")

    total_linhas = 0
    inseridos = 0
    atualizados = 0
    erros = []

    for linha in leitor:
        total_linhas += 1
        try:
            produto_id = int(linha["produto_id"])
            unidade_id = int(linha["unidade_id"])
            preco = float(str(linha["preco"]).replace(",", "."))

            produto = db.query(Produto).filter(Produto.id == produto_id).first()
            unidade = db.query(UnidadeMercado).filter(UnidadeMercado.id == unidade_id).first()

            if not produto:
                erros.append(f"Linha {total_linhas}: produto_id {produto_id} nao encontrado.")
                continue

            if not unidade:
                erros.append(f"Linha {total_linhas}: unidade_id {unidade_id} nao encontrada.")
                continue

            existente = db.query(PrecoProduto).filter(
                PrecoProduto.produto_id == produto_id,
                PrecoProduto.unidade_id == unidade_id).first()

            historico = HistoricoPreco(produto_id=produto_id, unidade_id=unidade_id, preco=preco)
            db.add(historico)

            if existente:
                existente.preco = preco
                atualizados += 1
            else:
                novo = PrecoProduto(produto_id=produto_id, unidade_id=unidade_id, preco=preco)
                db.add(novo)
                inseridos += 1

        except Exception as e:
            erros.append(f"Linha {total_linhas}: erro ao processar ({str(e)}).")

    db.commit()

    return {
        "arquivo": arquivo.filename,
        "total_linhas": total_linhas,
        "inseridos": inseridos,
        "atualizados": atualizados,
        "erros": erros,
    }


@router.get("/precos", response_model=list[PrecoProdutoRead])
def listar_precos(db: Session = Depends(get_db)):
    return db.query(PrecoProduto).all()


@router.get("/historico-precos", response_model=list[HistoricoPrecoRead])
def listar_historico_precos(db: Session = Depends(get_db)):
    return db.query(HistoricoPreco).order_by(HistoricoPreco.id.desc()).all()


@router.get("/comparacao/cidade/{cidade_id}/lista/{lista_id}", response_model=ComparacaoCidadeResponse)
def comparar_por_cidade(
    cidade_id: int,
    lista_id: int,
    db: Session = Depends(get_db)):
    lista = db.query(ListaCompra).filter(
        ListaCompra.id == lista_id,
        True
    ).first()

    if not lista:
        raise HTTPException(status_code=404, detail="Lista nao encontrada.")

    resultado = comparar_lista_por_cidade(db, lista_id, cidade_id)
    if not resultado["lista_nome"]:
        raise HTTPException(status_code=404, detail="Lista nao encontrada.")
    return resultado


@router.get("/comparacao/cidade/{cidade_id}/lista/{lista_id}/otimizada", response_model=ComparacaoCidadeOtimizadaResponse)
def comparar_por_cidade_otimizada(
    cidade_id: int,
    lista_id: int,
    db: Session = Depends(get_db)):
    lista = db.query(ListaCompra).filter(
        ListaCompra.id == lista_id,
        True
    ).first()

    if not lista:
        raise HTTPException(status_code=404, detail="Lista nao encontrada.")

    resultado = comparar_lista_otimizada_por_cidade(db, lista_id, cidade_id)
    if not resultado["lista_nome"]:
        raise HTTPException(status_code=404, detail="Lista nao encontrada.")
    return resultado


@router.get("/resumo/cidade/{cidade_id}/lista/{lista_id}", response_model=ResumoInteligenteResponse)
def resumo_inteligente(
    cidade_id: int,
    lista_id: int,
    db: Session = Depends(get_db)):
    lista = db.query(ListaCompra).filter(
        ListaCompra.id == lista_id,
        True
    ).first()

    if not lista:
        raise HTTPException(status_code=404, detail="Lista nao encontrada.")

    resultado = gerar_resumo_inteligente_compra(db, lista_id, cidade_id)
    if not resultado:
        raise HTTPException(status_code=404, detail="Lista nao encontrada.")
    return resultado




@router.get("/produtos/busca")
def buscar_produtos(q: str = "", limit: int = 20, db: Session = Depends(get_db)):
    query = db.query(Produto)

    if q:
        query = query.filter(Produto.nome.ilike(f"%{q}%"))

    produtos = query.limit(limit).all()

    return [
        {
            "id": p.id,
            "nome": p.nome
        }
        for p in produtos
    ]


@router.delete("/itens/{item_id}")
def deletar_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(ItemListaCompra).filter(
        ItemListaCompra.id == item_id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item nao encontrado")

    db.delete(item)
    db.commit()
    return {"ok": True, "message": "Item removido com sucesso"}



@router.put("/listas/{lista_id}", response_model=ListaCompraRead)
def atualizar_lista(
    lista_id: int,
    payload: dict,
    db: Session = Depends(get_db)
):
    item = db.query(ListaCompra).filter(ListaCompra.id == lista_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Lista nao encontrada")

    nome = payload.get("nome")
    if nome:
        item.nome = nome

    db.commit()
    db.refresh(item)
    return item


@router.delete("/listas/{lista_id}")
def deletar_lista(
    lista_id: int,
    db: Session = Depends(get_db)
):
    item = db.query(ListaCompra).filter(ListaCompra.id == lista_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Lista nao encontrada")

    db.query(ItemListaCompra).filter(ItemListaCompra.lista_id == lista_id).delete()
    db.delete(item)
    db.commit()

    return {"ok": True, "message": "Lista removida com sucesso"}


@router.get("/listas/{lista_id}/resumo")
def resumo_lista(lista_id: int, db: Session = Depends(get_db)):
    itens = db.query(ItemListaCompra).filter_by(lista_id=lista_id).all()

    total_itens = len(itens)
    total_quantidade = sum(i.quantidade for i in itens)

    total_custo = 0.0

    for item in itens:
        preco_atual = (
            db.query(PrecoProduto)
            .filter(PrecoProduto.produto_id == item.produto_id)
            .order_by(PrecoProduto.id.desc())
            .first()
        )

        preco_valor = None

        if preco_atual:
            preco_valor = float(preco_atual.preco)
        else:
            historico = (
                db.query(HistoricoPreco)
                .filter(HistoricoPreco.produto_id == item.produto_id)
                .order_by(HistoricoPreco.id.desc())
                .first()
            )
            if historico:
                preco_valor = float(historico.preco)

        if preco_valor is not None:
            total_custo += preco_valor * item.quantidade

    return {
        "total_itens": total_itens,
        "total_quantidade": total_quantidade,
        "custo_estimado": round(total_custo, 2)
    }

@router.get("/produtos/busca-com-precos")
def buscar_produtos_com_precos(termo: str, db: Session = Depends(get_db)):
    termo = (termo or "").strip()

    if len(termo) < 2:
        return []

    produtos = (
        db.query(Produto)
        .filter(Produto.nome.ilike(f"%{termo}%"))
        .order_by(Produto.nome.asc())
        .limit(8)
        .all()
    )

    resultado = []

    for produto in produtos:
        melhor_preco = (
            db.query(PrecoProduto, UnidadeMercado)
            .join(UnidadeMercado, PrecoProduto.unidade_id == UnidadeMercado.id)
            .filter(PrecoProduto.produto_id == produto.id)
            .order_by(PrecoProduto.preco.asc())
            .first()
        )

        item = {
            "id": produto.id,
            "nome": produto.nome,
            "mercado": None,
            "preco": None
        }

        if melhor_preco:
            preco_obj, unidade_obj = melhor_preco
            item["mercado"] = unidade_obj.nome
            item["preco"] = float(preco_obj.preco)

        resultado.append(item)

    return resultado
