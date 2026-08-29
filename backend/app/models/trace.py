# app/models/trace.py
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, JSON, Text, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Trace(Base):
    __tablename__ = "traces"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    passages_recuperes = Column(JSON, nullable=True)
    scores_recherche = Column(JSON, nullable=True)
    outils_appeles = Column(JSON, nullable=True)
    ml_input_output = Column(JSON, nullable=True)
    reponse_finale = Column(Text, nullable=True)
    latence_ms = Column(Integer, nullable=True)
    erreurs = Column(String, nullable=True)
    date = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("SessionConversation", back_populates="traces")
    reponse = relationship("Reponse", back_populates="trace", uselist=False)