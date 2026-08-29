# app/api/routes/chat.py
import logging
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.agent.agent import process_message
from app.core.database import get_db
from app.repositories.trace_repository import save_interaction
from app.services.log_writer import log_response

logger = logging.getLogger(__name__)
routeur = APIRouter()


class ChatRequest(BaseModel):
    session_id: str
    message: str = Field(..., min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    reponse: str
    sources: List[Dict[str, Any]] = []
    outils_executes: List[Dict[str, Any]] = []
    incertitude: str
    avertissements: List[str] = []
    temps_execution_s: float
    session_id: Optional[str] = None
    cache_hit: Optional[bool] = None
    bloquee: Optional[bool] = None


# app/api/routes/chat.py
def _split_trace_for_log(result: Dict[str, Any]) -> Dict[str, Any]:
    outils = result.get("outils_executes", [])
    ml_step = next((o for o in outils if o.get("outil") == "analyser_profil_ml"), {})
    onto_step = next((o for o in outils if o.get("outil") == "verifier_prerequis"), {})

    ml_res = ml_step.get("resultat", {}) if isinstance(ml_step.get("resultat"), dict) else {}
    onto_res = onto_step.get("resultat", {}) if isinstance(onto_step.get("resultat"), dict) else {}
    onto_params = onto_step.get("parametres", {}) if isinstance(onto_step.get("parametres"), dict) else {}

    return {
        "rag": {
            "reponse": result.get("reponse"),
            "incertitude": result.get("incertitude"),
            "temps_execution_s": result.get("temps_execution_s"),
            "avertissements": result.get("avertissements", []),
        },
        "ontology": {
            "profil_extrait": {
                # Tool INPUT, not output — verifier_prerequis's `prerequis_requis`
                # output field is always [] today (see symbolic_tools.py docstring).
                "competences": onto_params.get("competences", []),
                "centres_interet": onto_params.get("centres_interet", []),
            },
            "formation_demandee": onto_params.get("formation"),
            "eligible": onto_res.get("eligible"),
            "raisonnement": onto_res.get("raisonnement"),
        },
        "ml": {
            "success": ml_res.get("statut") == "ok",
            "orientation": (ml_res.get("predictions") or [{}])[0].get("parcours"),
            "probabilites": ml_res.get("predictions", []),
            "execution_time": result.get("temps_execution_s"),
        },
    }

@routeur.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    result = process_message(req.session_id, req.message)

    try:
        save_interaction(db, req.session_id, req.message, result)
    except Exception as e:
        logger.error(f"Échec de la sauvegarde en base : {e}")

    try:
        log_response(_split_trace_for_log(result))
    except Exception as e:
        logger.error(f"Échec de l'écriture du log fichier : {e}")

    return result