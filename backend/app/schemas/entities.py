from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LoginRequest(BaseModel):
    email: str
    senha: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UsuarioCreate(BaseModel):
    nome: str
    email: str | None = None
    senha: str | None = None


class UsuarioRead(BaseModel):
    id: int
    nome: str
    email: str | None = None
    model_config = ConfigDict(from_attributes=True)


class EstadoCreate(BaseModel):
    nome: str
    uf: str


class EstadoRead(EstadoCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class CidadeCreate(BaseModel):
    nome: str
    estado_id: int


class CidadeRead(CidadeCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class RedeMercadoCreate(BaseModel):
    nome: str


class RedeMercadoRead(RedeMercadoCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class UnidadeMercadoCreate(BaseModel):
    rede_id: int
    cidade_id: int
    nome: str
    endereco: str | None = None
    cep: str | None = None


class UnidadeMercadoRead(UnidadeMercadoCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class CategoriaCreate(BaseModel):
    nome: str


class CategoriaRead(CategoriaCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class ProdutoCreate(BaseModel):
    assinatura: str | None = None
    assinatura: str | None = None
    nome: str
    categoria_id: int | None = None


class ProdutoRead(ProdutoCreate):
    assinatura: str | None = None
    id: int
    model_config = ConfigDict(from_attributes=True)


class ListaModeloCreate(BaseModel):
    usuario_id: int
    nome: str


class ListaModeloRead(ListaModeloCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class ItemListaModeloCreate(BaseModel):
    lista_modelo_id: int
    produto_id: int
    quantidade: int = 1


class ItemListaModeloRead(ItemListaModeloCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class ListaCompraCreate(BaseModel):
    usuario_id: int | None = None
    nome: str


class ListaCompraRead(ListaCompraCreate):
    id: int
    gerada_de_modelo_id: int | None = None
    gerada_em: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


class ItemListaCompraCreate(BaseModel):
    lista_id: int
    produto_id: int
    quantidade: int = 1


class ItemListaCompraRead(ItemListaCompraCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class PrecoProdutoCreate(BaseModel):
    produto_id: int
    unidade_id: int
    preco: float


class PrecoProdutoRead(PrecoProdutoCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class HistoricoPrecoRead(BaseModel):
    id: int
    produto_id: int
    unidade_id: int
    preco: float
    criado_em: datetime
    model_config = ConfigDict(from_attributes=True)


class ComparacaoCidadeItem(BaseModel):
    produto_id: int
    produto_nome: str
    quantidade: int
    preco_unitario: float | None = None
    subtotal: float | None = None
    disponivel: bool


class ComparacaoCidadeUnidade(BaseModel):
    unidade_id: int
    unidade_nome: str
    rede_nome: str
    cidade_id: int
    total: float
    itens_encontrados: int
    itens_faltantes: int
    completo: bool
    itens: list[ComparacaoCidadeItem]


class ComparacaoCidadeResponse(BaseModel):
    lista_id: int
    lista_nome: str
    cidade_id: int
    melhor_unidade_id: int | None
    melhor_unidade_nome: str | None
    melhor_rede_nome: str | None
    melhor_total: float | None
    unidades: list[ComparacaoCidadeUnidade]


class OtimizacaoCidadeItem(BaseModel):
    produto_id: int
    produto_nome: str
    quantidade: int
    unidade_id: int | None
    unidade_nome: str | None
    rede_nome: str | None
    preco_unitario: float | None
    subtotal: float | None
    disponivel: bool


class ComparacaoCidadeOtimizadaResponse(BaseModel):
    lista_id: int
    lista_nome: str
    cidade_id: int
    total_otimizado: float
    melhor_unidade_id: int | None
    melhor_unidade_nome: str | None
    melhor_rede_nome: str | None
    melhor_total: float | None
    economia_vs_melhor_unidade: float | None
    itens_encontrados: int
    itens_faltantes: int
    completo: bool
    itens: list[OtimizacaoCidadeItem]


class ResumoInteligenteResponse(BaseModel):
    lista_id: int
    lista_nome: str
    cidade_id: int
    melhor_unidade_id: int | None
    melhor_unidade_nome: str | None
    melhor_rede_nome: str | None
    total_melhor_unidade: float | None
    total_otimizado: float
    economia_valor: float | None
    economia_percentual: float | None
    quantidade_mercados_otimizados: int
    vale_dividir_compra: bool
    recomendacao: str
