from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from app.repositories.utilisateur_repository import UtilisateurRepository
from app.core.config import settings
from fastapi import HTTPException, status
from app.models import Utilisateur

pwd_context = CryptContext(
    schemes=["argon2"],
    argon2id__default_rounds=3,
    argon2id__default_memory_cost=65536,
    argon2id__default_parallelism=4,
    deprecated="auto",
)


def creer_token(data: dict):
    payload = data.copy()
    expiration = datetime.utcnow() + timedelta(minutes=480)
    payload.update({"exp": expiration})

    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


class AuthService:
    def __init__(self, utilisateur_repository: UtilisateurRepository):
        self.utilisateur_repository = utilisateur_repository

    def authentifier(self, email, mot_de_passe):
        utilisateur = self.utilisateur_repository.get_by_email(email)

        if utilisateur:
            mot_de_passe_correct = pwd_context.verify(
                mot_de_passe, utilisateur.mot_de_passe
            )

            if mot_de_passe_correct:
                data = {"id": utilisateur.id, "role": utilisateur.role}

                return {"token": creer_token(data), "role": utilisateur.role}
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Identifiant invalide",
                )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="identifiant invalide"
        )

    def inscrire(self, email, nom, prenom,mot_de_passe):
        if self.utilisateur_repository.get_by_email(email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email déjà existant"
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
        }
