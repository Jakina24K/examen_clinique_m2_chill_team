"""
app/tools/ml_tools.py
------------------------
Paradigme "Single LLM" : cet outil ne fait AUCUN appel LLM. Il reçoit un
profil déjà structuré par l'agent et le mappe directement vers les 76
colonnes MODEL_FEATURES, via ml.src.predict.predict_from_features.
"""

import logging
from typing import Any, Dict, List, Literal, Optional

from langchain_core.tools import tool
from pydantic import BaseModel, Field, model_validator

from ml.src.predict import predict_from_features, MODEL_FEATURES, PredictionError

logger = logging.getLogger(__name__)


class ProfilInput(BaseModel):
    matieres_preferees: List[str] = Field(default_factory=list, description="Matières explicitement déclarées")
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
        if self.statut == "ok" and not self.predictions:
            raise ValueError("statut='ok' exige au moins une prédiction dans `predictions`.")
        if self.statut == "profil_insuffisant" and not self.message:
            raise ValueError("statut='profil_insuffisant' exige un `message` explicatif.")
        return self


# ==========================================================================
# Mapping texte-libre (déjà extrait par l'agent) -> colonnes MODEL_FEATURES.
# POINT DE DÉPART pour l'équipe ML — cette table de correspondance mot-clé
# est volontairement simple et doit être étoffée/validée par vous ; je n'ai
# pas de visibilité sur l'importance réelle des features à l'entraînement.
# ==========================================================================

KEYWORD_TO_FEATURE: Dict[str, str] = {
    "mathématiques": "niveau_mathématiques", "maths": "niveau_mathématiques",
    "algèbre": "niveau_algèbre", "analyse": "niveau_analyse",
    "programmation": "niveau_informatique", "informatique": "niveau_informatique",
    "développement": "niveau_informatique", "développeur": "niveau_informatique",
    "algorithme": "niveau_algorithme", "base de données": "niveau_base_de_données",
    "html": "niveau_html_css", "css": "niveau_html_css",
    "physique": "niveau_physique", "chimie": "niveau_chimie",
    "biologie": "niveau_biologie_animale", "économie": "niveau_economie",
    "finance": "niveau_finance_publique", "comptabilité": "niveau_comptabilité",
    "droit": "niveau_droit", "marketing": "niveau_marketing",
    "anglais": "niveau_anglais", "statistique": "niveau_statistiques_appliquée",
}

COMPETENCE_TO_FEATURE: Dict[str, str] = {
    "résolution de problèmes": "analyse_synthese", "esprit critique": "analyse_synthese",
    "analyse": "analyse_synthese", "rigueur": "analyse_synthese",
    "travail en équipe": "travail_equipe", "collaboration": "travail_equipe",
    "autonomie": "autonomie", "initiative": "autonomie",
    "créativité": "creativite", "innovation": "creativite",
    "gestion de projet": "gestion_projet", "leadership": "gestion_projet",
}

NEUTRAL_LEVEL, MATCHED_LEVEL = 2, 4  # échelle 1-5 utilisée à l'entraînement
DEFAULT_CATEGORICALS: Dict[str, Any] = {
    "age": 23, "statut": 0, "bac_serie": 1, "environnement": 4, "secteur": 0,
}


def _map_profil_to_features(matieres: List[str], competences: List[str], interets: List[str]) -> Dict[str, Any]:
    features: Dict[str, Any] = dict(DEFAULT_CATEGORICALS)
    for col in MODEL_FEATURES:
        if col.startswith("niveau_"):
            features[col] = NEUTRAL_LEVEL
    for term in [t.lower() for t in matieres + interets]:
        for kw, col in KEYWORD_TO_FEATURE.items():
            if kw in term or term in kw:
                features[col] = MATCHED_LEVEL
    for col in ("travail_equipe", "autonomie", "analyse_synthese", "creativite", "gestion_projet"):
        features[col] = 0
    for comp in [c.lower() for c in competences]:
        for kw, col in COMPETENCE_TO_FEATURE.items():
            if kw in comp or comp in kw:
                features[col] = MATCHED_LEVEL
    return features


@tool("analyser_profil_ml", args_schema=ProfilInput)
def analyser_profil_ml(
    matieres_preferees: Optional[List[str]] = None,
    competences: Optional[List[str]] = None,
    centres_interet: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Prédit un parcours à partir du profil déjà extrait par l'agent — aucun
    appel LLM ici. GARDE-FOU : jamais de sexe/âge/origine comme feature.
    """
    matieres_preferees = matieres_preferees or []
    competences = competences or []
    centres_interet = centres_interet or []

    if not (matieres_preferees or competences or centres_interet):
        return AnalyserProfilOutput(
            statut="profil_insuffisant",
            message="Profil trop incomplet pour une prédiction fiable.",
        ).model_dump()

    try:
        result = predict_from_features(_map_profil_to_features(matieres_preferees, competences, centres_interet))
    except PredictionError as e:
        logger.error("Erreur classifieur ML", exc_info=True)
        return AnalyserProfilOutput(statut="profil_insuffisant", message=str(e)).model_dump()

    predictions = [MLPrediction(**p) for p in result["predictions"]]
    if not predictions:
        return AnalyserProfilOutput(statut="profil_insuffisant", message="Aucune prédiction exploitable.").model_dump()

    return AnalyserProfilOutput(
        statut="ok",
        modele="orientia_best_model_v2 (sklearn)",
        predictions=predictions,
        indice_confiance=predictions[0].probabilite,
        features_utilisees={
            "matieres_preferees": matieres_preferees,
            "competences": competences,
            "centres_interet": centres_interet,
        },
    ).model_dump()