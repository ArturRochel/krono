from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
import app.models
from app.routers.krono import router as krono_router  # <-- 1. Importa o router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Krono API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(krono_router)  # <-- 2. Registra as rotas na aplicação


@app.get("/health")
def health_check():
    return {"app": "Krono", "status": "ok"}