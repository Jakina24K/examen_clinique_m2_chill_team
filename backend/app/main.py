"""
app/main.py
-------------
Point d'entrée FastAPI ORIENT'IA.

Paradigme "Single LLM Orchestrator" : le seul appel LLM autorisé dans tout
le backend est celui de l'agent LangChain (app/agent/agent.py). RAG, ML et
IA symbolique sont déterministes et appelés UNIQUEMENT comme outils de
l'agent — jamais directement depuis une route HTTP par un utilisateur final.

/api/orientation/predict et /api/recommandation/dynamique restent exposés,
sans LLM, pour permettre à l'équipe ML/Symbolique de tester leurs pipelines
en isolation. Le chemin utilisateur normal est exclusivement POST /api/chat.
"""

# app/main.py — top of file, before anything else
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

def setup_logging() -> None:
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(fmt)
    file_handler = RotatingFileHandler(
        LOG_DIR / "orientia.log", maxBytes=5_000_000, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(fmt)

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers.clear()
    root.addHandler(stream_handler)
    root.addHandler(file_handler)
    logging.captureWarnings(True)   # route warnings.warn(...) through logging too

    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        lg = logging.getLogger(name)
        lg.handlers.clear()
        lg.propagate = True

setup_logging()
logger = logging.getLogger("app.main")

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.routes import auth, chat, ontology
from app.core.database import engine, get_db
from app.schemas.orientation import OrientationRequest
from app.services.recommandation_service import recommandation_service
import asyncio
from app.agent.agent import _get_agent_executor,cleanup_expired_sessions
from app.rag.retriever import _get_vectorstore
from ml.src.predict import predict_from_features, warmup as ml_warmup, is_ready as ml_is_ready

import warnings
from sklearn.exceptions import InconsistentVersionWarning

# Masque les avertissements d'incompatibilité de version de scikit-learn
warnings.filterwarnings("ignore", category=InconsistentVersionWarning)

async def _session_cleanup_loop() -> None:
    while True:
        await asyncio.sleep(600)  # every 10 min
        try:
            cleanup_expired_sessions()
        except Exception:
            logger.error("Échec du nettoyage périodique des sessions", exc_info=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- 1. Base de données ---
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            logger.info("🟢 [DATABASE] Connexion à PostgreSQL réussie.")
    except Exception as e:
        logger.error(f"🔴 [DATABASE] Échec de la connexion : {e}")

    # --- 2. Ontologie RDF — dégradation gracieuse si le .ttl est absent.
    # Appel SANS argument : recommandation_service.load_ontology() résout
    # déjà le chemin relativement à __file__, pas au cwd du process.
    try:
        recommandation_service.load_ontology()
        logger.info(f"🟢 [RDFLIB] Ontologie chargée ({len(recommandation_service.graph)} triplets).")
    except Exception as e:
        logger.error(f"🔴 [RDFLIB] Échec du chargement — verifier_prerequis répondra en dégradé : {e}")

    # --- 3. RAG + ML + Agent, chargés une seule fois avant d'accepter du trafic ---
    logger.info("⏳ Chargement du vectorstore, du pipeline ML et de l'agent...")
    try:
        _get_vectorstore()
    except Exception as e:
        logger.error(f"🔴 [RAG] Échec du chargement du vectorstore : {e}")

    try:
        ml_warmup()
    except Exception as e:
        logger.error(f"🔴 [ML] Échec du chargement du pipeline sklearn — analyser_profil_ml répondra en dégradé : {e}")

    try:
        _get_agent_executor()
        logger.info("🟢 Agent ORIENT'IA prêt.")
    except Exception as e:
        logger.error(f"🔴 [AGENT] Échec de l'initialisation de l'agent : {e}")

    cleanup_task = asyncio.create_task(_session_cleanup_loop())
    yield
    cleanup_task.cancel()


app = FastAPI(
    title="ORIENT'IA - Assistant d'orientation pédagogique",
    description="Agent IA d'orientation (RAG + ML + IA Symbolique), orchestré par un unique agent LangChain.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # remplacer par l'origine réelle du frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.routeur, prefix="/api/auth", tags=["Authentification"])
app.include_router(ontology.routeur, prefix="/api/recommandation", tags=["Ontology (debug, sans LLM)"])
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
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")


@app.get("/health/ml", tags=["Health"])
def health_check_ml():
    return {"status": "ok" if ml_is_ready() else "not_loaded"}


@app.post("/api/orientation/predict", tags=["Orientation IA (debug, sans LLM)"])
def predict_orientation_direct(request: OrientationRequest):
    """
    Test direct du pipeline sklearn, sans agent ni appel LLM — prend un
    profil déjà structuré. Utile à l'équipe ML pour valider le modèle en
    isolation. Le chemin utilisateur normal est POST /api/chat.
    """
    try:
        return {"success": True, **predict_from_features(request.model_dump())}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {str(e)}")