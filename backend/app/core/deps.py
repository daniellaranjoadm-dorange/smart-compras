from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db.base import SessionLocal
from app.models.entities import Usuario
from app.core.security import decodificar_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = decodificar_access_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Token invalido")

    if not payload:
        raise HTTPException(status_code=401, detail="Token invalido ou expirado")

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="Token sem usuario")

    usuario = None

    # primeiro tenta como ID numerico
    try:
        usuario = db.query(Usuario).filter(Usuario.id == int(sub)).first()
    except Exception:
        usuario = None

    # se nao achar, tenta como email
    if not usuario:
        usuario = db.query(Usuario).filter(Usuario.email == str(sub)).first()

    if not usuario:
        raise HTTPException(status_code=401, detail="Usuario nao encontrado")

    return usuario
