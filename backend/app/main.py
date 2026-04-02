from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.api.routes import router
from app.api import auth
from app.db.base import engine
from app.models.entities import Base
from app.routes import admin

app = FastAPI(title="Smart Compras API", version="0.1.0")

app.include_router(router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(admin.router)

BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "Smart Compras API online"}


@app.get("/app")
def app_web():
    return FileResponse(WEB_DIR / "index.html")
