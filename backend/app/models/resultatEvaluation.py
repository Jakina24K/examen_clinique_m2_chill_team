import enum
import uuid
from datetime import datetime
# Importer ForeignKey, JSON, Text et func depuis sqlalchemy
from sqlalchemy import Column, String, Boolean, DateTime, Enum, Integer, ForeignKey, JSON, Text, func, Float
from app.core.database import Base

class ResultatEvaluation(Base):
    __tablename__ = "resultats_evaluation"

    id = Column(Integer, primary_key=True, index=True)
    cas_test_id = Column(Integer, ForeignKey("cas_test.id"), nullable=False)
    reponse_obtenue = Column(Text, nullable=True)
    sources_citees = Column(JSON, nullable=True)
    outils_appeles = Column(JSON, nullable=True)
    score = Column(Float, nullable=True)
    version_systeme = Column(String, nullable=True)
    date = Column(DateTime(timezone=True), server_default=func.now())