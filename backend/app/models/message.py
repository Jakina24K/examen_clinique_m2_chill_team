# app/models/message.py
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    role = Column(String, nullable=False)
    contenu = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("SessionConversation", back_populates="messages")
    reponse = relationship("Reponse", back_populates="message", uselist=False)