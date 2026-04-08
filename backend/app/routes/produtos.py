from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entities import Produto, Categoria

router = APIRouter(prefix="/api/catalogo/produtos", tags=["catalogo"])


@router.get("")
def listar_produtos_catalogo(
    categoria: str | None = Query(default=None),
    q: str | None = Query(default=None),
    limit: int = Query(default=50, le=200),
    db: Session = Depends(get_db),
):
    query = db.query(Produto, Categoria).outerjoin(Categoria, Produto.categoria_id == Categoria.id)

    if categoria:
        query = query.filter(Categoria.nome == categoria)

    if q:
        query = query.filter(Produto.nome.ilike(f"%{q}%"))

    resultados = query.order_by(Produto.nome.asc()).limit(limit).all()

    return [
        {
            "id": produto.id,
            "nome": produto.nome,
            "categoria": categoria_obj.nome if categoria_obj else None,
        }
        for produto, categoria_obj in resultados
    ]
