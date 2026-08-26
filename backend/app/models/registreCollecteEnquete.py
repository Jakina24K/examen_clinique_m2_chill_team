import enum
import uuid
from datetime import datetime
# Importer ForeignKey, JSON, Text et func depuis sqlalchemy
from sqlalchemy import Column, String, Boolean, DateTime, Enum, Integer, ForeignKey, JSON, Text, func
from app.core.database import Base

class RegistreCollecteEnquete(Base):
    __tablename__ = "registre_collecte_enquete"

    id = Column(Integer, primary_key=True, index=True)
    questionnaire_version = Column(String, nullable=False)
    population = Column(String, nullable=False)  # etudiants, professionnels
    mode_diffusion = Column(String, nullable=True)
    date_debut = Column(DateTime, nullable=False)
    date_fin = Column(DateTime, nullable=True)
    nb_recues = Column(Integer, default=0)
    nb_retenues = Column(Integer, default=0)
    nb_ecartees = Column(Integer, default=0)
    consentement_texte = Column(Text, nullable=False)