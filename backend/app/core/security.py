from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from jose import jwt, JWTError
from app.core.config import settings
from app.repositories.utilisateur_repository import UtilisateurRepository
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    utilisateur_repository = UtilisateurRepository(db)
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré"
        )
    
    utilisateur = utilisateur_repository.get_by_id(payload["id"])

    if not utilisateur:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail= "L'utilisateur n'existe pas."
        )

    return utilisateur

def require_demandeur(current_user = Depends(get_current_user)):
    if current_user.role != "demandeur":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Connecté mais non autorisé"
        )
    
    return current_user

def require_recepteur(current_user = Depends(get_current_user)):
    if current_user.role != "recepteur":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Connecté mais non autorisé"
        )
    
    return current_user
