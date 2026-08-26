from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class Categorie(str, Enum):
    COMPTES_AUTH = "Comptes et authentification"
    RESEAU_CONNECTIVITE = "Réseau et connectivité"
    MATERIEL = "Matériel informatique"
    LOGICIELS = "Logiciels et applications"
    IMPRIMANTES = "Imprimantes et périphériques"
    DROITS_ACCES = "Droits d'accès"
    CYBERSECURITE = "Cybersécurité"
    AUTRE = "Autre ou indéterminé"


class Priorite(str, Enum):
    BASSE = "basse"
    MOYENNE = "moyenne"
    HAUTE = "haute"
    CRITIQUE = "critique"


class ActionFinale(str, Enum):
    RESOLUTION = "resolution"
    DEMANDE_INFO = "demande_information"
    ESCALADE = "escalade"


class SourceRAG(BaseModel):
    doc_id: str = Field(..., description="ID de la fiche KB ou ticket source")
    titre: str = Field(..., description="Titre de la fiche")
    score_pertinence: float = Field(..., description="Score de pertinence (0.0 à 1.0)")
    extrait: Optional[str] = Field(None, description="Extrait utile du document")


class ToolCallLog(BaseModel):
    outil: str = Field(..., description="Nom de l'outil exécuté")
    parametres_json: str = Field("{}", description="Paramètres d'entrée au format chaîne JSON")
    statut: str = Field(..., description="Statut de l'exécution (succes, echec)")
    resultat: Optional[str] = Field(None, description="Résultat retourné par l'outil")


class TicketInput(BaseModel):
    ticket_id: str = Field(..., example="TCK-1001")
    description: str = Field(..., example="Impossible de me connecter au VPN depuis ce matin.")
    utilisateur: str = Field("user_anon", example="jean.dupont")


class AgentResponseSchema(BaseModel):
    resume_incident: str
    categorie: Categorie
    priorite: Priorite
    equipe_affectee: str
    indice_confiance: float
    diagnostic_propose: str
    informations_manquantes: List[str] = Field(default_factory=list)
    action: ActionFinale
    validation_humaine_requise: bool
    raison_validation: Optional[str] = None
    etapes_resolution: List[str] = Field(default_factory=list)
    sources: List[SourceRAG] = Field(default_factory=list)
    outils_executes: List[ToolCallLog] = Field(default_factory=list)