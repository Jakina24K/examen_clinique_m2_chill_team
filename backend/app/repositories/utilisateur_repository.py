from app.models.utilisateur import Utilisateur
from sqlalchemy.orm import Session

class UtilisateurRepository:
    def __init__(self, db : Session):
        self.db = db

    def get_by_email(self, email: str):
        return self.db.query(Utilisateur).filter(Utilisateur.email == email).first()
    
    def get_by_id(self, id: str):
        return self.db.query(Utilisateur).filter(Utilisateur.id == id).first()
    
    def create(self, utilisateur: Utilisateur):
        self.db.add(utilisateur)
        self.db.commit()
        self.db.refresh(utilisateur)
        return utilisateur