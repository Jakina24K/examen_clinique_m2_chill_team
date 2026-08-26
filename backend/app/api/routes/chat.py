# app/api/routes/chat.py
from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.agent.agent import process_message

routeur = APIRouter()

class ChatRequest(BaseModel):
    session_id: str
    message: str
    # On limite entre 1 et 2000 caractères
    message: str = Field(..., min_length=1, max_length=2000)

@routeur.post("/chat")
def chat(req: ChatRequest):
    return process_message(req.session_id, req.message)