"""
app/tools/symbolic_tools.py
------------------------------
Consomme des paramètres structurés déjà fournis par l'agent et interroge
l'ontologie RDF réelle (recommandation_service / SPARQL) — aucun LLM ici.

LIMITE CONNUE : la requête SPARQL disponible classe les parcours par nombre
de compétences correspondantes (:developpe), sans distinguer "prérequis
obligatoire" de "compétence développée". eligible/prerequis_manquants sont
donc une APPROXIMATION tant que cette distinction n'est pas confirmée dans
l'ontologie — voir _check_eligibility.
"""

import logging
from typing import Any, Dict, List, Literal, Optional

from langchain_core.tools import tool
from pydantic import BaseModel, Field, model_validator

from app.services.recommandation_service import recommandation_service

logger = logging.getLogger(__name__)


class VerifierPrerequisInput(BaseModel):
    formation: str = Field(..., description="Nom du parcours (ex: 'ParcoursIA')")
    competences: List[str] = Field(..., description="Identifiants de compétences déjà extraits par l'agent")


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
        if self.statut == "ok" and (self.formation is None or self.eligible is None):
            raise ValueError("statut='ok' exige `formation` et `eligible`.")
        if self.statut == "formation_inconnue" and not self.message:
            raise ValueError("statut='formation_inconnue' exige un `message`.")
        return self


def _check_eligibility(formation: str, competences: List[str]) -> Dict[str, Any]:
    resultats = recommandation_service.get_recommandation_dynamique(competences=competences)
    match = next(
        (r for r in resultats if r["parcours"].strip().lower() == formation.strip().lower()),
        None,
    )
    if match is None:
        return {"trouve": False, "eligible": False, "score": 0}
    return {"trouve": True, "eligible": match["scoreCorrespondance"] > 0, "score": match["scoreCorrespondance"]}


@tool("verifier_prerequis", args_schema=VerifierPrerequisInput)
def verifier_prerequis(formation: str, competences: List[str]) -> Dict[str, Any]:
    """
    Vérifie via SPARQL (aucun LLM) si un parcours correspond aux compétences
    déclarées. L'agent doit fournir `competences` déjà structurées.
    """
    try:
        result = _check_eligibility(formation, competences)
    except Exception as e:
        logger.error("Erreur requête ontologie", exc_info=True)
        return VerifierPrerequisOutput(
            statut="formation_inconnue",
            message=f"Impossible d'interroger l'ontologie ({type(e).__name__}).",
            formations_connues=[],
        ).model_dump()

    if not result["trouve"]:
        return VerifierPrerequisOutput(
            statut="formation_inconnue",
            message=f"'{formation}' non trouvé dans l'ontologie pour ces compétences. Ne pas inventer de parcours.",
            formations_connues=[],
        ).model_dump()

    return VerifierPrerequisOutput(
        statut="ok",
        formation=formation,
        prerequis_requis=[],
        prerequis_manquants=[],
        eligible=result["eligible"],
        raisonnement=f"{result['score']} compétence(s) correspondante(s) (approximation par correspondance, pas une vérification stricte de prérequis).",
    ).model_dump()