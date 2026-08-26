import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.params import Depends
from sqlalchemy.orm import Session
from app.schemas_tickets.ticket import TicketInput, AgentResponseSchema
from app.agent.agent import process_ticket
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

@app.post("/api/tickets/process", response_model=AgentResponseSchema)
def handle_ticket(ticket: TicketInput):
    """Endpoint principal de traitement de ticket."""
    try:
        start_time = time.time()
        result = process_ticket(ticket)
        execution_time = round(time.time() - start_time, 2)
        print(f"Ticket {ticket.ticket_id} traité en {execution_time}s")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))