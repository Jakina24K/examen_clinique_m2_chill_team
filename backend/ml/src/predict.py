"""
ml/src/predict.py
--------------------
Point d'entrée UNIQUE pour le pipeline sklearn. Chargement paresseux et
partagé : main.py (endpoint debug) et app/tools/ml_tools.py (agent)
importent tous les deux depuis ce module — aucun autre fichier ne doit
appeler joblib.load() sur ces artefacts.

Ne dépend plus de ml.src.preprocessing / extract_prompt : ces modules
faisaient un second appel Gemini (extract_orientation_data) ou supposaient
un format de colonnes brut issu d'un export Google Forms — aucun des deux
ne correspond à l'entrée structurée que fournit désormais l'agent.
"""

import logging
from typing import Any, Dict, List

import joblib
import pandas as pd

logger = logging.getLogger(__name__)

MODEL_PATH = "ml/models/orientia_best_model_v2.pkl"
SCALER_PATH = "ml/models/orientia_scaler_v2.pkl"
SELECTOR_PATH = "ml/models/orientia_selector_v2.pkl"
MAPPING_PATH = "ml/models/orientia_id_to_filiere.pkl"

MODEL_FEATURES: List[str] = [
    "age", "statut", "bac_serie",
    "niveau_agronomie", "niveau_algorithme", "niveau_algèbre", "niveau_analyse",
    "niveau_analyse_mathématique", "niveau_anglais", "niveau_assainissement",
    "niveau_autocad", "niveau_bactériologie", "niveau_base_de_données",
    "niveau_biochimie", "niveau_biologie_animale", "niveau_biologie_cellulaire",
    "niveau_botanique", "niveau_chimie", "niveau_comptabilité", "niveau_dessin",
    "niveau_droit", "niveau_ecologie", "niveau_economie", "niveau_econométrie",
    "niveau_electricité", "niveau_electronique", "niveau_environnement",
    "niveau_enzymologie", "niveau_finance_publique", "niveau_fiscalité",
    "niveau_français", "niveau_génétique", "niveau_géologie", "niveau_html_css",
    "niveau_hydraulique", "niveau_hygiène", "niveau_industries_pharmaceutiques",
    "niveau_informatique", "niveau_informatique_scientifique", "niveau_langage_c",
    "niveau_logique", "niveau_macroéconomie_microéconomie", "niveau_maintenance",
    "niveau_marketing", "niveau_mathématique_discrète", "niveau_mathématique_financière",
    "niveau_mathématiques", "niveau_musique", "niveau_mécanique",
    "niveau_nutrition_humaine", "niveau_organisation_dentreprise",
    "niveau_ouvrages_métalliques", "niveau_pharmacologie", "niveau_physiologie_animale",
    "niveau_physiologie_végétale", "niveau_physique", "niveau_probabilité_statistique",
    "niveau_pétrologie", "niveau_science_des_aliments", "niveau_sites_touristiques",
    "niveau_statistiques_appliquée", "niveau_structure_de_données",
    "niveau_structure_des_ordinateurs", "niveau_technique_bancaire",
    "niveau_thermodynamique", "niveau_thermophysique", "niveau_virologie",
    "niveau_zootechnie", "travail_equipe", "autonomie", "analyse_synthese",
    "creativite", "gestion_projet", "environnement", "secteur",
]

_model = _scaler = _selector = _id_to_filiere = None


class PredictionError(Exception):
    """Erreur métier du pipeline ML — attrapée par ml_tools.py, jamais
    laissée remonter comme une exception sklearn/pandas opaque."""


def _load() -> None:
    global _model, _scaler, _selector, _id_to_filiere
    if _model is not None:
        return
    logger.info("Chargement du pipeline ML (scaler/selector/modèle/mapping)...")
    _scaler = joblib.load(SCALER_PATH)
    _selector = joblib.load(SELECTOR_PATH)
    _model = joblib.load(MODEL_PATH)
    _id_to_filiere = joblib.load(MAPPING_PATH)
    if hasattr(_model, "n_features_in_") and len(MODEL_FEATURES) != _model.n_features_in_:
        logger.warning(
            f"MODEL_FEATURES a {len(MODEL_FEATURES)} colonnes, "
            f"le modèle en attend {_model.n_features_in_}."
        )
    logger.info("Pipeline ML chargé.")


def warmup() -> None:
    """Appelé explicitement depuis main.py:lifespan avant d'accepter du trafic."""
    _load()


def is_ready() -> bool:
    return _model is not None


def predict_from_features(feature_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    `feature_dict` doit être keyed par (un sous-ensemble de) MODEL_FEATURES,
    valeurs numériques. Colonnes manquantes -> 0. Lève PredictionError avec
    un message clair plutôt qu'une exception sklearn/pandas opaque.
    """
    _load()
    try:
        df = pd.DataFrame([feature_dict]).reindex(columns=MODEL_FEATURES, fill_value=0)
        df = df.apply(pd.to_numeric, errors="coerce").fillna(0)

        if df.shape[1] != _scaler.n_features_in_:
            raise PredictionError(
                f"{df.shape[1]} colonnes fournies, le scaler en attend {_scaler.n_features_in_}."
            )

        X_selected = _selector.transform(_scaler.transform(df))
        orientation_id = int(_model.predict(X_selected)[0])
        orientation = _id_to_filiere.get(orientation_id, f"Filière inconnue (ID {orientation_id})")

        predictions: List[Dict[str, Any]] = []
        if hasattr(_model, "predict_proba"):
            proba = _model.predict_proba(X_selected)[0]
            predictions = sorted(
                [
                    {
                        "parcours": _id_to_filiere.get(int(_model.classes_[i]), str(_model.classes_[i])),
                        "probabilite": round(float(proba[i]), 3),
                    }
                    for i in range(len(proba))
                ],
                key=lambda x: x["probabilite"],
                reverse=True,
            )

        return {"orientation": orientation, "predictions": predictions}
    except PredictionError:
        raise
    except Exception as e:
        raise PredictionError(f"{type(e).__name__}: {e}") from e