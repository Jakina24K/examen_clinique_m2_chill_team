from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.utilisateur import RoleEnum, Utilisateur
from app.repositories.utilisateur_repository import UtilisateurRepository

# URL correspondant au préfixe de vos routes d'authentification
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> Utilisateur:
    utilisateur_repository = UtilisateurRepository(db)
    
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        # Compatibilité : extrait 'sub' en priorité, sinon 'id'
        user_id: str = payload.get("sub") or payload.get("id")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Jeton invalide : identifiant manquant",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Jeton invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )

    utilisateur = utilisateur_repository.get_by_id(user_id)

    if not utilisateur:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="L'utilisateur n'existe pas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not utilisateur.actif:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte utilisateur désactivé",
        )

    return utilisateur


def require_demandeur(
    current_user: Annotated[Utilisateur, Depends(get_current_user)]
) -> Utilisateur:
    # Extraire la valeur string de l'enum de manière sécurisée
    role_val = current_user.role.value if isinstance(current_user.role, RoleEnum) else current_user.role
    
    if role_val != RoleEnum.demandeur.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux demandeurs",
        )
    return current_user


def require_recepteur(
    current_user: Annotated[Utilisateur, Depends(get_current_user)]
) -> Utilisateur:
    role_val = current_user.role.value if isinstance(current_user.role, RoleEnum) else current_user.role
    
    if role_val != RoleEnum.recepteur.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux récepteurs",
        )
    return current_user