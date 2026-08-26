import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class RoleEnum(str, enum.Enum):
    demandeur = "demandeur"
    recepteur = "recepteur"

class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id         = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    nom        = Column(String(100), nullable=False)
    prenom     = Column(String(100), nullable=False)
    email      = Column(String(150), unique=True, nullable=False)
    mot_de_passe = Column(String(255), nullable=False)
    role       = Column(Enum(RoleEnum), nullable=False, default=RoleEnum.demandeur)
    actif      = Column(Boolean, default=True)
    departement_id = Column(String, ForeignKey("departements.id"),nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tickets_demandes = relationship("Ticket",foreign_keys="Ticket.demandeur_id", back_populates="demandeur")
    tickets_recus = relationship("Ticket", foreign_keys="Ticket.recepteur_id",back_populates="recepteur")
    departement = relationship("Departement", back_populates="utilisateur")


