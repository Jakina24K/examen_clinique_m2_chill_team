# app/api/routes/chat.py
from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.agent.agent import process_message
from app.api.routes.ontology import get_recommandation_from_prompt
from ml.src.predict import predict_orientation
routeur = APIRouter()

class ChatRequest(BaseModel):
    session_id: str
    # On limite entre 1 et 2000 caractères
    message: str = Field(..., min_length=1, max_length=2000)

@routeur.post("/chat")
def chat(req: ChatRequest):
    resultat_rag = process_message(req.session_id, req.message)
    resultat_ontology = get_recommandation_from_prompt(req.message)
    resultat_ml = predict_orientation(req.message)

    return {
        "rag": resultat_rag,
        "ontology": resultat_ontology,
        "ml": resultat_ml
    }