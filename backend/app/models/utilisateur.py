import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id         = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    nom        = Column(String(100), nullable=False)
    prenom     = Column(String(100), nullable=False)
    email      = Column(String(150), unique=True, nullable=False)
    mot_de_passe = Column(String(255), nullable=False)
    actif      = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)



