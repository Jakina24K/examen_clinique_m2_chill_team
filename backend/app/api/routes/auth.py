from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories.utilisateur_repository import UtilisateurRepository
from app.schemas.auth_schema import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    CurrentUserResponse
)
from app.services.auth_service import AuthService
from app.core.security import get_current_user

routeur = APIRouter()


@routeur.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    utilisateur_repository = UtilisateurRepository(db)

    auth_service = AuthService(utilisateur_repository)

    resultat = auth_service.authentifier(
        email=request.email, mot_de_passe=request.mot_de_passe
    )

    return resultat


@routeur.post("/register", response_model=RegisterResponse)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    utilisateur_repository = UtilisateurRepository(db)

    auth_service = AuthService(utilisateur_repository)

    resultat = auth_service.inscrire(
        email=request.email,
        nom=request.nom,
        prenom=request.prenom,
        mot_de_passe=request.mot_de_passe,
    )

    return resultat

@routeur.get("/me", response_model=CurrentUserResponse)
def me(payload = Depends(get_current_user)):
    return payload
