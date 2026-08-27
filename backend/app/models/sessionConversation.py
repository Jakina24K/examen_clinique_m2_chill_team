import enum
import uuid
from datetime import datetime
# Importer ForeignKey, JSON, Text et func depuis sqlalchemy
from sqlalchemy import Column, String, Boolean, DateTime, Enum, Integer, ForeignKey, JSON, Text, func, relationship
from app.core.database import Base


class SessionConversation(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    date_debut = Column(DateTime(timezone=True), server_default=func.now())
    utilisateur_id = Column(String, ForeignKey("utilisateur.id"), nullable=True)

    messages = relationship("Message", back_populates="session")
    reponses = relationship("Reponse", back_populates = "session")
    traces = relationship("Trace", back_populates = "session")