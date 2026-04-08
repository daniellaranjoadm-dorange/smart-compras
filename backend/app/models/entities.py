from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(120), index=True)
    email: Mapped[str | None] = mapped_column(String(150), unique=True, nullable=True)
    senha_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)


class Estado(Base):
    __tablename__ = "estados"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    uf: Mapped[str] = mapped_column(String(2), unique=True, index=True)


class Cidade(Base):
    __tablename__ = "cidades"
    __table_args__ = (
        UniqueConstraint("nome", "estado_id", name="uq_cidade_estado"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(120), index=True)
    estado_id: Mapped[int] = mapped_column(ForeignKey("estados.id"))

    estado = relationship("Estado")


class RedeMercado(Base):
    __tablename__ = "redes_mercado"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(120), unique=True, index=True)


class UnidadeMercado(Base):
    __tablename__ = "unidades_mercado"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    rede_id: Mapped[int] = mapped_column(ForeignKey("redes_mercado.id"))
    cidade_id: Mapped[int] = mapped_column(ForeignKey("cidades.id"))
    nome: Mapped[str] = mapped_column(String(150), index=True)
    endereco: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cep: Mapped[str | None] = mapped_column(String(12), nullable=True)

    rede = relationship("RedeMercado")
    cidade = relationship("Cidade")


class Categoria(Base):
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(120), unique=True, index=True)


class Produto(Base):
    __tablename__ = "produtos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(120), index=True)
    categoria_id: Mapped[int | None] = mapped_column(ForeignKey("categorias.id"), nullable=True)
    assinatura: Mapped[str | None] = mapped_column(nullable=True, index=True)

    categoria = relationship("Categoria")


class ListaModelo(Base):
    __tablename__ = "listas_modelo"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    nome: Mapped[str] = mapped_column(String(150), index=True)

    usuario = relationship("Usuario")


class ItemListaModelo(Base):
    __tablename__ = "itens_lista_modelo"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    lista_modelo_id: Mapped[int] = mapped_column(ForeignKey("listas_modelo.id"))
    produto_id: Mapped[int] = mapped_column(ForeignKey("produtos.id"))
    quantidade: Mapped[int] = mapped_column(Integer, default=1)

    lista_modelo = relationship("ListaModelo")
    produto = relationship("Produto")


class ListaCompra(Base):
    __tablename__ = "listas_compra"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    nome: Mapped[str] = mapped_column(String(150), index=True)
    gerada_de_modelo_id: Mapped[int | None] = mapped_column(ForeignKey("listas_modelo.id"), nullable=True)
    gerada_em: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)

    usuario = relationship("Usuario")
    modelo = relationship("ListaModelo")


class ItemListaCompra(Base):
    __tablename__ = "itens_lista_compra"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    lista_id: Mapped[int] = mapped_column(ForeignKey("listas_compra.id"))
    produto_id: Mapped[int] = mapped_column(ForeignKey("produtos.id"))
    quantidade: Mapped[int] = mapped_column(Integer, default=1)

    lista = relationship("ListaCompra")
    produto = relationship("Produto")


class PrecoProduto(Base):
    __tablename__ = "precos_produto"
    __table_args__ = (
        UniqueConstraint("produto_id", "unidade_id", name="uq_preco_produto_unidade"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    produto_id: Mapped[int] = mapped_column(ForeignKey("produtos.id"))
    unidade_id: Mapped[int] = mapped_column(ForeignKey("unidades_mercado.id"))
    preco: Mapped[float] = mapped_column(Numeric(10, 2))

    produto = relationship("Produto")
    unidade = relationship("UnidadeMercado")


class HistoricoPreco(Base):
    __tablename__ = "historico_precos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    produto_id: Mapped[int] = mapped_column(ForeignKey("produtos.id"), index=True)
    unidade_id: Mapped[int] = mapped_column(ForeignKey("unidades_mercado.id"), index=True)
    preco: Mapped[float] = mapped_column(Numeric(10, 2))
    criado_em: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())

    produto = relationship("Produto")
    unidade = relationship("UnidadeMercado")

