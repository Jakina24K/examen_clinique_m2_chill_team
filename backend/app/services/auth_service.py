from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone
from app.repositories.utilisateur_repository import UtilisateurRepository
from app.core.config import settings
from fastapi import HTTPException, status
from app.models.utilisateur import Utilisateur

pwd_context = CryptContext(
    schemes=["argon2"],
    argon2id__default_rounds=3,
    argon2id__default_memory_cost=65536,
    argon2id__default_parallelism=4,
    deprecated="auto",
)


def creer_token(data: dict) -> str:
    payload = data.copy()
    expiration = datetime.now(timezone.utc) + timedelta(minutes=480)
    payload.update({"exp": expiration})

    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


class AuthService:
    def __init__(self, utilisateur_repository: UtilisateurRepository):
        self.utilisateur_repository = utilisateur_repository

    def authentifier(self, email: str, mot_de_passe: str) -> dict:
        utilisateur = self.utilisateur_repository.get_by_email(email)

        # 1. Vérification unifiée (Email + Mot de passe)
        if not utilisateur or not pwd_context.verify(mot_de_passe, utilisateur.mot_de_passe):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Identifiant ou mot de passe incorrect",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 2. Vérification que le compte n'est pas désactivé
        if not utilisateur.actif:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Compte utilisateur désactivé",
            )

        # 3. Conversion explicite du RoleEnum en str pour le JWT
        role_str = str(utilisateur.role.value if hasattr(utilisateur.role, "value") else utilisateur.role)

        data = {
            "sub": str(utilisateur.id),  # Norme RFC 7519 pour l'identifiant sujet
            "role": role_str,
        }

        return {
            "token": creer_token(data),
            "token_type": "bearer",
            "role": role_str,
        }

    def inscrire(self, email: str, nom: str, prenom: str, mot_de_passe: str) -> dict:
        if self.utilisateur_repository.get_by_email(email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email déjà existant",
            )

        mot_de_passe_hashe = pwd_context.hash(mot_de_passe)
        utilisateur = Utilisateur(
            nom=nom,
            prenom=prenom,
            email=email,
            mot_de_passe=mot_de_passe_hashe,
        )

        nouvel_utilisateur = self.utilisateur_repository.create(utilisateur)

        return {
            "id": nouvel_utilisateur.id,
            "nom": nouvel_utilisateur.nom,
            "prenom": nouvel_utilisateur.prenom,
            "email": nouvel_utilisateur.email,
            "role": str(nouvel_utilisateur.role.value if hasattr(nouvel_utilisateur.role, "value") else nouvel_utilisateur.role),
        }