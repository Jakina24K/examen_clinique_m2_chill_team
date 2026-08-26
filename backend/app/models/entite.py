import enum
import uuid
from datetime import datetime
# Importer ForeignKey, JSON, Text et func depuis sqlalchemy
from sqlalchemy import Column, String, Boolean, DateTime, Enum, Integer, ForeignKey, JSON, Text, func
from app.core.database import Base

class Entite(Base):
    __tablename__ = "entites"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)  # Etudiant, Formation, Parcours, Matiere,
                                            # Competence, Prerequis, Metier, CentreInteret
    nom = Column(String, nullable=False)