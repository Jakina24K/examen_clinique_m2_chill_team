import enum
import uuid
from datetime import datetime
# Importer ForeignKey, JSON, Text et func depuis sqlalchemy
from sqlalchemy import Column, String, Boolean, DateTime, Enum, Integer, ForeignKey, JSON, Text, func, relationship
from app.core.database import Base

class ProfilCentreInteret(Base):
    __tablename__ = "profils_centres_interet"

    profil_id = Column(Integer, ForeignKey("profils.id"), primary_key=True)
    centre_interet_id = Column(Integer, ForeignKey("centres_interet.id"), primary_key=True)

    profil = relationship("Profil", back_populates="centres_interet")
    centre_interet = relationship("CentreInteret")