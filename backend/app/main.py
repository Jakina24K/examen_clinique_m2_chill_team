import time
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.agent.agent import process_ticket
from app.api.routes import auth
from app.core.database import engine, get_db
from app.schemas_tickets.ticket import AgentResponseSchema, TicketInput


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Logique d'initialisation (remplace @app.on_event("startup"))
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            print("🟢 [DATABASE] Connexion à PostgreSQL réussie avec succès !")
    except Exception as e:
        print(f"🔴 [DATABASE] Échec de la connexion à PostgreSQL : {e}")
    yield


app = FastAPI(
    title="ORIENT'IA - IT Support Agent",
    description="Agent d'assistance IT intelligent (LLM + RAG + Tools + Guardrails)",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montage du routeur sous /api/auth pour correspondre à tokenUrl="/api/auth/login" dans security.py
app.include_router(auth.routeur, prefix="/api/auth", tags=["Authentification"])


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "mAIntenance & Assistance AI Agent"}


@app.get("/health/db", tags=["Health"])
def health_check_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Database connection error: {str(e)}"
        )


@app.post(
    "/api/tickets/process",
    response_model=AgentResponseSchema,
    tags=["Agent IT"],
)
def handle_ticket(ticket: TicketInput):
    """Endpoint principal de traitement de ticket par l'agent IA."""
    try:
        start_time = time.time()
        result = process_ticket(ticket)
        execution_time = round(time.time() - start_time, 2)
        print(f"Ticket {ticket.ticket_id} traité en {execution_time}s")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))