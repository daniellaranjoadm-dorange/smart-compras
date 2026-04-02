from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.base import SessionLocal
from app.models.entities import Usuario
from app.core.security import decodificar_access_token

security = HTTPBearer()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    payload = decodificar_access_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Token invalido")

    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Token sem usuario")

    usuario = db.query(Usuario).filter(Usuario.email == email).first()

    if not usuario:
        raise HTTPException(status_code=401, detail="Usuario nao encontrado")

    return usuario
