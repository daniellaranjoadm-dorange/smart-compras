from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.api import auth
from app.db.base import engine
from app.models.entities import Base
from app.routes import admin
from app.routes import produtos
from app.routes import comparacao
from app.routes import cesta

BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"

app = FastAPI(title="Smart Compras API", version="0.1.0")

app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")

app.include_router(router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(admin.router)
app.include_router(produtos.router)
app.include_router(comparacao.router)
app.include_router(cesta.router)

def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "Smart Compras API online"}


@app.get("/app")
def app_web():
    return FileResponse(WEB_DIR / "index.html")


@app.get("/smart-comparacao.css")
def smart_comparacao_css():
    file_path = WEB_DIR / "smart-comparacao.css"
    if not file_path.exists():
        return FileResponse(WEB_DIR / "index.html")
    return FileResponse(file_path)


@app.get("/smart-comparacao.js")
def smart_comparacao_js():
    file_path = WEB_DIR / "smart-comparacao.js"
    if not file_path.exists():
        return FileResponse(WEB_DIR / "index.html")
    return FileResponse(file_path)
