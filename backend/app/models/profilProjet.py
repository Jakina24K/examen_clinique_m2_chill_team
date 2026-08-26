import enum
import uuid
from datetime import datetime
# Importer ForeignKey, JSON, Text et func depuis sqlalchemy
from sqlalchemy import Column, String, Boolean, DateTime, Enum, Integer, ForeignKey, JSON, Text, func, relationship
from app.core.database import Base

class ProfilProjet(Base):
    __tablename__ = "profils_projets"

    id = Column(Integer, primary_key=True, index=True)
    profil_id = Column(Integer, ForeignKey("profils.id"), nullable=False)
    description_projet = Column(Text, nullable=False)

    profil = relationship("Profil", back_populates="projets")