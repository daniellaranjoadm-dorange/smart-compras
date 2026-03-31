from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
import csv
import io

from app.db.base import Base, engine
from app.db.session import get_db
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
    Usuario,
)
from app.schemas.entities import (
    CategoriaCreate,
    CategoriaRead,
    CidadeCreate,
    CidadeRead,
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
    UsuarioRead,
)
from app.services.comparacao_local import (
    comparar_lista_otimizada_por_cidade,
    comparar_lista_por_cidade,
    gerar_resumo_inteligente_compra,
)

Base.metadata.create_all(bind=engine)

router = APIRouter()


@router.post("/usuarios", response_model=UsuarioRead)
def criar_usuario(payload: UsuarioCreate, db: Session = Depends(get_db)):
    item = Usuario(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/usuarios", response_model=list[UsuarioRead])
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(Usuario).order_by(Usuario.nome).all()


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
def listar_listas_modelo(db: Session = Depends(get_db), usuario_id: int | None = None):
    query = db.query(ListaModelo)
    if usuario_id is not None:
        query = query.filter(ListaModelo.usuario_id == usuario_id)
    return query.order_by(ListaModelo.nome).all()


@router.post("/itens-lista-modelo", response_model=ItemListaModeloRead)
def criar_item_lista_modelo(payload: ItemListaModeloCreate, db: Session = Depends(get_db)):
    item = ItemListaModelo(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/itens-lista-modelo", response_model=list[ItemListaModeloRead])
def listar_itens_lista_modelo(db: Session = Depends(get_db), lista_modelo_id: int | None = None):
    query = db.query(ItemListaModelo)
    if lista_modelo_id is not None:
        query = query.filter(ItemListaModelo.lista_modelo_id == lista_modelo_id)
    return query.all()


@router.post("/listas", response_model=ListaCompraRead)
def criar_lista(payload: ListaCompraCreate, db: Session = Depends(get_db)):
    item = ListaCompra(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/listas", response_model=list[ListaCompraRead])
def listar_listas(db: Session = Depends(get_db), usuario_id: int | None = None):
    query = db.query(ListaCompra)
    if usuario_id is not None:
        query = query.filter(ListaCompra.usuario_id == usuario_id)
    return query.order_by(ListaCompra.nome).all()


@router.post("/listas-modelo/{lista_modelo_id}/gerar", response_model=ListaCompraRead)
def gerar_lista_de_modelo(lista_modelo_id: int, db: Session = Depends(get_db)):
    modelo = db.query(ListaModelo).filter(ListaModelo.id == lista_modelo_id).first()
    if not modelo:
        raise HTTPException(status_code=404, detail="Lista modelo nao encontrada.")

    agora = datetime.now()
    nome_lista = f"{modelo.nome} - {agora.strftime('%Y-%m-%d')}"

    nova_lista = ListaCompra(
        usuario_id=modelo.usuario_id,
        nome=nome_lista,
        gerada_de_modelo_id=modelo.id,
        gerada_em=agora,
    )
    db.add(nova_lista)
    db.commit()
    db.refresh(nova_lista)

    itens_modelo = db.query(ItemListaModelo).filter(ItemListaModelo.lista_modelo_id == modelo.id).all()

    for item in itens_modelo:
        novo_item = ItemListaCompra(
            lista_id=nova_lista.id,
            produto_id=item.produto_id,
            quantidade=item.quantidade,
        )
        db.add(novo_item)

    db.commit()
    db.refresh(nova_lista)
    return nova_lista


@router.post("/itens", response_model=ItemListaCompraRead)
def criar_item(payload: ItemListaCompraCreate, db: Session = Depends(get_db)):
    item = ItemListaCompra(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/itens", response_model=list[ItemListaCompraRead])
def listar_itens(db: Session = Depends(get_db)):
    return db.query(ItemListaCompra).all()


@router.post("/precos", response_model=PrecoProdutoRead)
def criar_preco(payload: PrecoProdutoCreate, db: Session = Depends(get_db)):
    existente = db.query(PrecoProduto).filter(
        PrecoProduto.produto_id == payload.produto_id,
        PrecoProduto.unidade_id == payload.unidade_id,
    ).first()

    historico = HistoricoPreco(
        produto_id=payload.produto_id,
        unidade_id=payload.unidade_id,
        preco=payload.preco,
    )
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
                PrecoProduto.unidade_id == unidade_id,
            ).first()

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
def comparar_por_cidade(cidade_id: int, lista_id: int, db: Session = Depends(get_db)):
    resultado = comparar_lista_por_cidade(db, lista_id, cidade_id)
    if not resultado["lista_nome"]:
        raise HTTPException(status_code=404, detail="Lista nao encontrada.")
    return resultado


@router.get("/comparacao/cidade/{cidade_id}/lista/{lista_id}/otimizada", response_model=ComparacaoCidadeOtimizadaResponse)
def comparar_por_cidade_otimizada(cidade_id: int, lista_id: int, db: Session = Depends(get_db)):
    resultado = comparar_lista_otimizada_por_cidade(db, lista_id, cidade_id)
    if not resultado["lista_nome"]:
        raise HTTPException(status_code=404, detail="Lista nao encontrada.")
    return resultado


@router.get("/resumo/cidade/{cidade_id}/lista/{lista_id}", response_model=ResumoInteligenteResponse)
def resumo_inteligente(cidade_id: int, lista_id: int, db: Session = Depends(get_db)):
    resultado = gerar_resumo_inteligente_compra(db, lista_id, cidade_id)
    if not resultado:
        raise HTTPException(status_code=404, detail="Lista nao encontrada.")
    return resultado
