from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.api.routes import router

app = FastAPI(title="Smart Compras API", version="0.1.0")

app.include_router(router, prefix="/api")

BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"


@app.get("/")
def root():
    return {"message": "Smart Compras API online"}


@app.get("/app")
def app_web():
    return FileResponse(WEB_DIR / "index.html")
