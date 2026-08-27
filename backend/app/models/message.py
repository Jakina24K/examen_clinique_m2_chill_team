import enum
import uuid
from datetime import datetime
# Importer ForeignKey, JSON, Text et func depuis sqlalchemy
from sqlalchemy import Column, String, Boolean, DateTime, Enum, Integer, ForeignKey, func, relationship
from app.core.database import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    role = Column(String, nullable=False)  # user, assistant
    contenu = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("SessionConversation", back_populates="messages")