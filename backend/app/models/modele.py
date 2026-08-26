import enum
import uuid
from datetime import datetime
# Importer ForeignKey, JSON, Text et func depuis sqlalchemy
from sqlalchemy import Column, String, Boolean, DateTime, Enum, Integer, ForeignKey, JSON, Text, func
from app.core.database import Base

class Modele(Base):
    __tablename__ = "modeles"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    version = Column(String, nullable=False)
    date_entrainement = Column(DateTime, nullable=False)
    hyperparametres = Column(JSON, nullable=True)
    chemin_fichier = Column(String, nullable=False)