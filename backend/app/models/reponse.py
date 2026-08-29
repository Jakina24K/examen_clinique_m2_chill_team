# app/models/reponse.py
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Reponse(Base):
    __tablename__ = "reponses"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False)
    trace_id = Column(Integer, ForeignKey("traces.id"), nullable=False)
    contenu = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("SessionConversation", back_populates="reponses")
    message = relationship("Message", back_populates="reponse")
    trace = relationship("Trace", back_populates="reponse")