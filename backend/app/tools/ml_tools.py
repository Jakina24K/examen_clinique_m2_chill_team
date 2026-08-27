"""
app/tools/ml_tools.py
------------------------
Outil Machine Learning : classification du profil étudiant vers un parcours.

MOCK ACTUEL : heuristique de correspondance mot-clé (à remplacer, voir TODO).
Le contrat de sortie (`AnalyserProfilOutput`) est indépendant de
l'implémentation : tant que le classifieur réel construit cet objet avant
de retourner, rien dans agent.py n'a besoin de changer.
"""

import logging
from typing import Any, Dict, List, Literal, Optional

from langchain_core.tools import tool
from pydantic import BaseModel, Field, model_validator

logger = logging.getLogger(__name__)


class ProfilInput(BaseModel):
    matieres_preferees: List[str] = Field(default_factory=list, description="Matières explicitement déclarées par l'étudiant")
    competences: List[str] = Field(default_factory=list, description="Compétences explicitement déclarées")
    centres_interet: List[str] = Field(default_factory=list, description="Centres d'intérêt explicitement déclarés")


class MLPrediction(BaseModel):
    parcours: str
    probabilite: float = Field(..., ge=0.0, le=1.0)


class AnalyserProfilOutput(BaseModel):
    statut: Literal["ok", "profil_insuffisant"]
    message: Optional[str] = None
    modele: Optional[str] = None
    predictions: List[MLPrediction] = Field(default_factory=list)
    indice_confiance: Optional[float] = Field(None, ge=0.0, le=1.0)
    features_utilisees: Optional[Dict[str, List[str]]] = None

    @model_validator(mode="after")
    def _coherence(self) -> "AnalyserProfilOutput":
        """Empêche un classifieur réel de renvoyer statut='ok' sans prédictions
        exploitables, ou statut='profil_insuffisant' sans message — exactement
        la classe d'erreur qui casserait la règle 8 du system prompt sans que
        rien ne le signale."""
        if self.statut == "ok" and not self.predictions:
            raise ValueError("statut='ok' exige au moins une prédiction dans `predictions`.")
        if self.statut == "profil_insuffisant" and not self.message:
            raise ValueError("statut='profil_insuffisant' exige un `message` explicatif.")
        return self


@tool("analyser_profil_ml", args_schema=ProfilInput)
def analyser_profil_ml(
    matieres_preferees: Optional[List[str]] = None,
    competences: Optional[List[str]] = None,
    centres_interet: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Appelle le modèle de Machine Learning de recommandation de parcours.
    Entrée : UNIQUEMENT le profil déclaré explicitement par l'étudiant
    (jamais un profil inféré du style d'écriture ou d'attributs sensibles).
    Sortie : distribution de probabilités sur les parcours + indice de confiance.

    GARDE-FOU : ce modèle ne doit jamais recevoir sexe/âge/origine comme feature.

    TODO (teammate ML) : remplacer le bloc MOCK par le vrai classifieur, ex.
        model = joblib.load("models/orientation_clf.pkl")
        proba = model.predict_proba(vectorizer.transform([features]))
    Tant que le résultat passe par `AnalyserProfilOutput(...)` avant le
    `return`, la validation ci-dessus protège le contrat automatiquement.
    """
    matieres_preferees = matieres_preferees or []
    competences = competences or []
    centres_interet = centres_interet or []

    if not (matieres_preferees or competences or centres_interet):
        return AnalyserProfilOutput(
            statut="profil_insuffisant",
            message="Profil trop incomplet pour une prédiction fiable — poser une question de clarification.",
        ).model_dump()

    # --- MOCK : heuristique simple servant de placeholder au vrai classifieur ---
    signal_data = {m.lower() for m in matieres_preferees + centres_interet}
    scores = {
        "ISAIA (IA & Data)": 0.15 + 0.25 * len(signal_data & {"mathématiques", "programmation", "data", "analyse de données", "ia"}),
        "IGGLIA (Génie Logiciel)": 0.15 + 0.25 * len(signal_data & {"programmation", "développement", "informatique"}),
        "Réseaux & Cybersécurité": 0.10 + 0.25 * len(signal_data & {"réseaux", "sécurité", "cybersécurité"}),
    }
    total = sum(scores.values()) or 1.0
    predictions = sorted(
        [{"parcours": k, "probabilite": round(v / total, 3)} for k, v in scores.items()],
        key=lambda x: x["probabilite"],
        reverse=True,
    )
    confiance = predictions[0]["probabilite"] if predictions else 0.0

    return AnalyserProfilOutput(
        statut="ok",
        modele="mock_heuristique_v0 (à remplacer par le classifieur entraîné)",
        predictions=predictions,
        indice_confiance=round(confiance, 3),
        features_utilisees={
            "matieres_preferees": matieres_preferees,
            "competences": competences,
            "centres_interet": centres_interet,
        },
    ).model_dump()