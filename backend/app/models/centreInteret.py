import enum
import uuid
from datetime import datetime
# Importer ForeignKey, JSON, Text et func depuis sqlalchemy
from sqlalchemy import Column, String, Boolean, DateTime, Enum, Integer, ForeignKey, JSON, Text, func
from app.core.database import Base

class CentreInteret(Base):
    __tablename__ = "centres_interet"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False, unique=True)