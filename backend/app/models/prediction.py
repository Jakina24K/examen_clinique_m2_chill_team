import enum
import uuid
from datetime import datetime
# Importer ForeignKey, JSON, Text et func depuis sqlalchemy
from sqlalchemy import Column, String, Boolean, DateTime, Enum, Integer, ForeignKey, JSON, Text, func, Float
from app.core.database import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    profil_id = Column(Integer, ForeignKey("profils.id"), nullable=False)
    parcours_id = Column(Integer, ForeignKey("parcours.id"), nullable=False)
    modele_id = Column(Integer, ForeignKey("modeles.id"), nullable=False)
    score_adequation = Column(Float, nullable=False)
    rang = Column(Integer, nullable=True)
    date = Column(DateTime(timezone=True), server_default=func.now())