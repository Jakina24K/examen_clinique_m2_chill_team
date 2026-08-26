from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.utilisateur import Utilisateur

class UtilisateurRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Optional[Utilisateur]:
        return self.db.query(Utilisateur).filter(Utilisateur.email == email).first()

    def get_by_id(self, user_id: str) -> Optional[Utilisateur]:
        return self.db.query(Utilisateur).filter(Utilisateur.id == user_id).first()

    def create(self, utilisateur: Utilisateur) -> Utilisateur:
        self.db.add(utilisateur)
        self.db.commit()
        self.db.refresh(utilisateur)
        return utilisateur

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Utilisateur]:
        return self.db.query(Utilisateur).offset(skip).limit(limit).all()

    def update(self, utilisateur: Utilisateur) -> Utilisateur:
        self.db.commit()
        self.db.refresh(utilisateur)
        return utilisateur