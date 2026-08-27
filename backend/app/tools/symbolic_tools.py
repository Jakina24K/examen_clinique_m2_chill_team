"""
app/tools/symbolic_tools.py
------------------------------
Outil IA Symbolique : vérification déterministe des prérequis via une
mini-ontologie Parcours -> Prérequis.

MOCK ACTUEL : dict Python plat, à remplacer par un vrai graphe (voir TODO).
"""

import logging
from typing import Any, Dict, List, Literal, Optional

from langchain_core.tools import tool
from pydantic import BaseModel, Field, model_validator

logger = logging.getLogger(__name__)

# TODO (teammate Symbolique) : remplacer par un vrai graphe (networkx / RDF /
# requêtes de logique de description) chargé depuis data/knowledge/. Tant que
# `verifier_prerequis` construit un `VerifierPrerequisOutput` avant de
# retourner, ce fichier est le SEUL endroit à modifier.
ONTOLOGIE_PREREQUIS: Dict[str, List[str]] = {
    "ISAIA": ["mathématiques niveau L2", "bases en programmation", "algèbre linéaire"],
    "IGGLIA": ["bases en programmation", "structures de données"],
    "Réseaux & Cybersécurité": ["réseaux informatiques de base", "systèmes d'exploitation"],
}


class VerifierPrerequisInput(BaseModel):
    formation: str = Field(..., description="Nom du parcours/formation (ex: 'ISAIA')")
    competences: List[str] = Field(..., description="Compétences que l'étudiant déclare posséder")


class VerifierPrerequisOutput(BaseModel):
    statut: Literal["ok", "formation_inconnue"]
    message: Optional[str] = None
    formations_connues: Optional[List[str]] = None
    formation: Optional[str] = None
    prerequis_requis: Optional[List[str]] = None
    prerequis_manquants: Optional[List[str]] = None
    eligible: Optional[bool] = None
    raisonnement: Optional[str] = None

    @model_validator(mode="after")
    def _coherence(self) -> "VerifierPrerequisOutput":
        if self.statut == "ok":
            missing = [f for f in ("formation", "prerequis_requis", "eligible") if getattr(self, f) is None]
            if missing:
                raise ValueError(f"statut='ok' exige les champs {missing}.")
        if self.statut == "formation_inconnue" and not self.message:
            raise ValueError("statut='formation_inconnue' exige un `message` explicatif.")
        return self


@tool("verifier_prerequis", args_schema=VerifierPrerequisInput)
def verifier_prerequis(formation: str, competences: List[str]) -> Dict[str, Any]:
    """
    Vérification déterministe (règles symboliques) des prérequis d'un parcours,
    via une mini-ontologie Parcours -> Prérequis. Contrairement au RAG/ML, ce
    résultat est 100% reproductible et explicable — aucune hallucination possible.
    """
    formation_key = next(
        (k for k in ONTOLOGIE_PREREQUIS if k.lower() == formation.strip().lower()),
        None,
    )
    if formation_key is None:
        return VerifierPrerequisOutput(
            statut="formation_inconnue",
            message=(
                f"'{formation}' n'existe pas dans l'ontologie ORIENT'IA. "
                f"Ne pas inventer de parcours : orienter l'utilisateur vers l'administration."
            ),
            formations_connues=list(ONTOLOGIE_PREREQUIS.keys()),
        ).model_dump()

    requis = ONTOLOGIE_PREREQUIS[formation_key]
    possedees = {c.strip().lower() for c in competences}
    manquants = [r for r in requis if r.lower() not in possedees]

    return VerifierPrerequisOutput(
        statut="ok",
        formation=formation_key,
        prerequis_requis=requis,
        prerequis_manquants=manquants,
        eligible=len(manquants) == 0,
        raisonnement=(
            f"{len(requis) - len(manquants)}/{len(requis)} prérequis satisfaits "
            f"(règle déterministe, indépendante du LLM)."
        ),
    ).model_dump()