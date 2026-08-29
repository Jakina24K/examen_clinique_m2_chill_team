# app/models/sessionConversation.py
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class SessionConversation(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, index=True)
    external_session_id = Column(String, unique=True, index=True, nullable=False)
    date_debut = Column(DateTime(timezone=True), server_default=func.now())
    utilisateur_id = Column(String, ForeignKey("utilisateurs.id"), nullable=True)

    messages = relationship("Message", back_populates="session")
    reponses = relationship("Reponse", back_populates="session")
    traces = relationship("Trace", back_populates="session")