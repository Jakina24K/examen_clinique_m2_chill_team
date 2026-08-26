from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.utilisateur import Utilisateur
from app.repositories.utilisateur_repository import UtilisateurRepository
from app.schemas.auth_schema import (
    CurrentUserResponse,
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
)
from app.services.auth_service import AuthService

routeur = APIRouter()


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Instancie le service et son repository via injection de dépendances."""
    repository = UtilisateurRepository(db)
    return AuthService(repository)


@routeur.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Connexion utilisateur",
)
def login(
    request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    return auth_service.authentifier(
        email=request.email,
        mot_de_passe=request.mot_de_passe,
    )


@routeur.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Inscription d'un utilisateur",
)
def register(
    request: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    return auth_service.inscrire(
        email=request.email,
        nom=request.nom,
        prenom=request.prenom,
        mot_de_passe=request.mot_de_passe,
    )


@routeur.get(
    "/me",
    response_model=CurrentUserResponse,
    status_code=status.HTTP_200_OK,
    summary="Profil de l'utilisateur connecté",
)
def me(current_user: Utilisateur = Depends(get_current_user)):
    return current_user