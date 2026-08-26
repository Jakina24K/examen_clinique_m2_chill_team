import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.params import Depends
from sqlalchemy.orm import Session
from app.api.routes import (
    auth
)
from sqlalchemy import text
from app.core.database import engine, get_db

app = FastAPI(
    title="mAIntenance & Assistance - IT Support Agent",
    description="Agent d'assistance IT intelligent (LLM + RAG + Tools + Guardrails)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.routeur, prefix="/auth", tags=["Authentification"])

@app.on_event("startup")
def verify_db_connection():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            print("🟢 [DATABASE] Connexion à PostgreSQL réussie avec succès !")
    except Exception as e:
        print(f"🔴 [DATABASE] Échec de la connexion à PostgreSQL : {e}")

@app.get("/")
def health_check():
    return {"status": "ok", "service": "mAIntenance & Assistance AI Agent"}

@app.get("/health/db", tags=["Health"])
def health_check_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")
