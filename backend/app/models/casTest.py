import enum
import uuid
from datetime import datetime
# Importer ForeignKey, JSON, Text et func depuis sqlalchemy
from sqlalchemy import Column, String, Boolean, DateTime, Enum, Integer, ForeignKey, JSON, Text, func
from app.core.database import Base

class CasTest(Base):
    __tablename__ = "cas_test"

    id = Column(Integer, primary_key=True, index=True)
    categorie = Column(String, nullable=False)
    # factuel, comparaison, ml, multi_sources, absence_info,
    # ambigu, securite_injection, biais, profilage_psychologique
    question = Column(Text, nullable=False)
    criteres_attendus = Column(Text, nullable=False)