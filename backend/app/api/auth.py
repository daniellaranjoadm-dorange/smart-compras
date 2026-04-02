from fastapi import APIRouter, HTTPException, Depends, Form
from sqlalchemy.orm import Session

from app.db.base import SessionLocal
from app.models.entities import Usuario
from app.core.security import gerar_hash_senha, verificar_senha, criar_access_token
from app.core.deps import get_current_user

router = APIRouter(tags=["auth"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/auth/register")
def register(
    nome: str = Form(...),
    email: str = Form(...),
    senha: str = Form(...),
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(Usuario.email == email).first()

    if usuario:
        raise HTTPException(status_code=400, detail="Email ja cadastrado")

    novo = Usuario(
        nome=nome,
        email=email,
        senha_hash=gerar_hash_senha(senha)
    )

    db.add(novo)
    db.commit()
    db.refresh(novo)

    return {
        "message": "Usuario criado com sucesso",
        "id": novo.id,
        "nome": novo.nome,
        "email": novo.email
    }


@router.post("/auth/login")
def login(
    email: str = Form(...),
    senha: str = Form(...),
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(Usuario.email == email).first()

    if not usuario:
        raise HTTPException(status_code=401, detail="Usuario nao encontrado")

    if not usuario.senha_hash:
        raise HTTPException(status_code=401, detail="Usuario sem senha cadastrada")

    if not verificar_senha(senha, usuario.senha_hash):
        raise HTTPException(status_code=401, detail="Senha invalida")

    token = criar_access_token({"sub": usuario.email})

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/auth/me")
def me(usuario: Usuario = Depends(get_current_user)):
    return {
        "id": usuario.id,
        "nome": usuario.nome,
        "email": usuario.email
    }
