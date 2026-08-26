import enum
import uuid
from datetime import datetime
# Importer ForeignKey, JSON, Text et func depuis sqlalchemy
from sqlalchemy import Column, String, Boolean, DateTime, Enum, Integer, ForeignKey, JSON, Text, func, relationship
from app.core.database import Base

class ProfilLabel(Base):
    """Étiquette réelle : parcours choisi/suivi + issue constatée."""
    __tablename__ = "profils_labels"

    id = Column(Integer, primary_key=True, index=True)
    profil_id = Column(Integer, ForeignKey("profils.id"), nullable=False, unique=True)
    parcours_id = Column(Integer, ForeignKey("parcours.id"), nullable=True)
    satisfaction = Column(Integer, nullable=True)  # étudiants, échelle ex. 1-5
    metier_actuel = Column(String, nullable=True)  # professionnels
    jugement_retrospectif = Column(Text, nullable=True)  # professionnels

    profil = relationship("Profil", back_populates="label")