import enum
import uuid
from datetime import datetime
# Importer ForeignKey, JSON, Text et func depuis sqlalchemy
from sqlalchemy import Column, String, Boolean, DateTime, Enum, Integer, ForeignKey, JSON, Text, func
from app.core.database import Base

class RelationOntologie(Base):
    __tablename__ = "relations"

    id = Column(Integer, primary_key=True, index=True)
    entite_source_id = Column(Integer, ForeignKey("entites.id"), nullable=False)
    predicat = Column(String, nullable=False)  # enseigne, developpe, prepareA,
                                                # necessite, possede, prefere, estRequisePour
    entite_cible_id = Column(Integer, ForeignKey("entites.id"), nullable=False)