from typing import List

from pydantic import BaseModel, Field

class OrientationRequest(BaseModel):
    statut: str = "Étudiant (actuellement en formation)"
    age: str = "21 - 25 ans"
    bac_serie: str = "Série C (Mathématiques)"
    niveau_genie_civil: float = Field(2, ge=1, le=5)
    niveau_mathematiques: float = Field(2, ge=1, le=5)
    niveau_programmation_informatique: float = Field(2, ge=1, le=5)
    niveau_physique: float = Field(2, ge=1, le=5)
    niveau_chimie_biologie: float = Field(2, ge=1, le=5)
    niveau_analyse: float = Field(2, ge=1, le=5)
    niveau_autocad: float = Field(2, ge=1, le=5)
    niveau_bactériologie: float = Field(2, ge=1, le=5)
    niveau_biochimie: float = Field(2, ge=1, le=5)
    niveau_biologie_animale: float = Field(2, ge=1, le=5)
    niveau_biologie_cellulaire: float = Field(2, ge=1, le=5)
    niveau_chimie: float = Field(2, ge=1, le=5)
    niveau_comptabilité: float = Field(2, ge=1, le=5)
    niveau_droit: float = Field(2, ge=1, le=5)
    niveau_economie: float = Field(2, ge=1, le=5)
    niveau_enzymologie: float = Field(2, ge=1, le=5)
    niveau_finance_publique: float = Field(2, ge=1, le=5)
    niveau_génétique: float = Field(2, ge=1, le=5)
    niveau_marketing: float = Field(2, ge=1, le=5)
    niveau_organisation_dentreprise: float = Field(2, ge=1, le=5)
    niveau_physiologie_animale: float = Field(2, ge=1, le=5)
    niveau_physiologie_végétale: float = Field(2, ge=1, le=5)
    niveau_probabilité_statistique: float = Field(2, ge=1, le=5)
    niveau_thermodynamique: float = Field(2, ge=1, le=5)
    niveau_virologie: float = Field(2, ge=1, le=5)
    competences: List[str] = Field(default_factory=list)
    environnement: str = "Mixte (Bureau / Télétravail)"
    secteur: str = "Autre (précisez)"

class ExtractRequest(BaseModel):
    text: str