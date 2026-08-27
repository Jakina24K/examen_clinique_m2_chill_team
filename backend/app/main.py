from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.routes import auth, ontology
from app.core.database import engine, get_db
from app.services.recommandation_service import recommandation_service
from app.api.routes import auth, chat   
from app.core.database import engine, get_db
from app.agent.agent import _get_agent_executor
from app.rag.retriever import _get_vectorstore

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            print("🟢 [DATABASE] Connexion à PostgreSQL réussie avec succès !")
    except Exception as e:
        print(f"🔴 [DATABASE] Échec de la connexion à PostgreSQL : {e}")
    try:
        recommandation_service.load_ontology("backend\\app\\ontology\\OrientIA.ttl")
        print("🟢 [RDFLIB] Ontologie OrientIA.ttl chargée avec succès !")
    except Exception as e:
        print(f"🔴 [RDFLIB] Échec du chargement de l'ontologie : {e}")

    # Warm up RAG + agent BEFORE accepting traffic — avoids the race condition
    # in the lazy singletons and front-loads cold-start latency to boot time.
    print("⏳ Chargement du vectorstore et de l'agent...")
    _get_vectorstore()
    _get_agent_executor()
    print("🟢 Agent ORIENT'IA prêt.")

    yield

app = FastAPI(
    title="ORIENT'IA - Assistant d'orientation pédagogique",
    description="Agent IA d'orientation (RAG + ML + IA Symbolique) avec persistance et journalisation",
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
app.include_router(ontology.routeur, prefix="/api/recommandation", tags=["ONTOLOGY"])
app.include_router(chat.routeur, prefix="/api", tags=["Chat"])

@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "ORIENT'IA - Assistant d'orientation"}


@app.get("/health/db", tags=["Health"])
def health_check_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Database connection error: {str(e)}"
        )


# @app.post(
#     "/api/tickets/process",
#     response_model=AgentResponseSchema,
#     tags=["Agent IT"],
# )
# def handle_ticket(ticket: TicketInput):
#     """Endpoint principal de traitement de ticket par l'agent IA."""
#     try:
#         start_time = time.time()
#         result = process_ticket(ticket)
#         execution_time = round(time.time() - start_time, 2)
#         print(f"Ticket {ticket.ticket_id} traité en {execution_time}s")
#         return result
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))