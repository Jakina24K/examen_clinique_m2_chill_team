import time
from fastapi import HTTPException

from app.schemas.orientation import OrientationRequest, ExtractRequest

from ml.src.preprocessing import preprocess_survey_data
from ml.src.extract_prompt import extract_orientation_data

import joblib
import pandas as pd

# ============================================================
# MODEL & MAPPING
# ============================================================

MODEL_PATH = "ml/models/orientia_best_model_v2.pkl"
SCALER_PATH = "ml/models/orientia_scaler_v2.pkl"
SELECTOR_PATH = "ml/models/orientia_selector_v2.pkl"
MAPPING_PATH = "ml/models/orientia_id_to_filiere.pkl"

scaler = joblib.load(SCALER_PATH)
selector = joblib.load(SELECTOR_PATH)

model = joblib.load(MODEL_PATH)
id_to_filiere = joblib.load(MAPPING_PATH)

# ============================================================
# LISTE DES COLONNES ATTENDUES PAR LE MODÈLE
# ============================================================
# Basée exactement sur le dataset d'entraînement
# Total : 76 colonnes (age, statut, bac_serie + 72 niveaux + 5 compétences + 2 contexte)

MODEL_FEATURES = [
    "age",
    "statut",
    "bac_serie",
    "niveau_agronomie",
    "niveau_algorithme",
    "niveau_algèbre",
    "niveau_analyse",
    "niveau_analyse_mathématique",
    "niveau_anglais",
    "niveau_assainissement",
    "niveau_autocad",
    "niveau_bactériologie",
    "niveau_base_de_données",
    "niveau_biochimie",
    "niveau_biologie_animale",
    "niveau_biologie_cellulaire",
    "niveau_botanique",
    "niveau_chimie",
    "niveau_comptabilité",
    "niveau_dessin",
    "niveau_droit",
    "niveau_ecologie",
    "niveau_economie",
    "niveau_econométrie",
    "niveau_electricité",
    "niveau_electronique",
    "niveau_environnement",
    "niveau_enzymologie",
    "niveau_finance_publique",
    "niveau_fiscalité",
    "niveau_français",
    "niveau_génétique",
    "niveau_géologie",
    "niveau_html_css",
    "niveau_hydraulique",
    "niveau_hygiène",
    "niveau_industries_pharmaceutiques",
    "niveau_informatique",
    "niveau_informatique_scientifique",
    "niveau_langage_c",
    "niveau_logique",
    "niveau_macroéconomie_microéconomie",
    "niveau_maintenance",
    "niveau_marketing",
    "niveau_mathématique_discrète",
    "niveau_mathématique_financière",
    "niveau_mathématiques",
    "niveau_musique",
    "niveau_mécanique",
    "niveau_nutrition_humaine",
    "niveau_organisation_dentreprise",
    "niveau_ouvrages_métalliques",
    "niveau_pharmacologie",
    "niveau_physiologie_animale",
    "niveau_physiologie_végétale",
    "niveau_physique",
    "niveau_probabilité_statistique",
    "niveau_pétrologie",
    "niveau_science_des_aliments",
    "niveau_sites_touristiques",
    "niveau_statistiques_appliquée",
    "niveau_structure_de_données",
    "niveau_structure_des_ordinateurs",
    "niveau_technique_bancaire",
    "niveau_thermodynamique",
    "niveau_thermophysique",
    "niveau_virologie",
    "niveau_zootechnie",
    "travail_equipe",
    "autonomie",
    "analyse_synthese",
    "creativite",
    "gestion_projet",
    "environnement",
    "secteur",
]

print(f"✅ {len(MODEL_FEATURES)} colonnes définies (attendues par le modèle)")

# Vérification du modèle
if hasattr(model, "n_features_in_"):
    print(f"✅ Le modèle attend {model.n_features_in_} features.")
    if len(MODEL_FEATURES) != model.n_features_in_:
        print(f"⚠️ ATTENTION : Mismatch ! MODEL_FEATURES a {len(MODEL_FEATURES)} colonnes, "
              f"mais le modèle en attend {model.n_features_in_}")
else:
    print("⚠️ Le modèle n'a pas d'attribut n_features_in_.")

def predict_orientation(request: ExtractRequest):
    data: OrientationRequest = extract_orientation_data(request)
    try:
        start_time = time.time()

        data["competences"] = ";".join(data["competences"])
        df = pd.DataFrame([data])

        # 2. Prétraiter : générer les 76 colonnes spécialisées
        X = preprocess_survey_data(df, MODEL_FEATURES)

        # Vérifier le nombre de colonnes
        if X.shape[1] != model.n_features_in_:
            # Le modèle attend le nombre de features après sélection, mais on va appliquer le sélecteur
            # On vérifie plutôt que le nombre de colonnes correspond à celui attendu par le scaler
            if X.shape[1] != scaler.n_features_in_:
                raise HTTPException(
                    status_code=500,
                    detail=f"Le preprocessing a produit {X.shape[1]} colonnes, "
                           f"mais le scaler en attend {scaler.n_features_in_}."
                )

        # 3. Normalisation
        X_scaled = scaler.transform(X)

        # 4. Sélection des features
        X_selected = selector.transform(X_scaled)

        # 5. Prédiction
        prediction = model.predict(X_selected)
        orientation_id = int(prediction[0])
        orientation = id_to_filiere.get(
            orientation_id, f"Filière inconnue (ID {orientation_id})"
        )

        # 6. Probabilités
        probabilities = []
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(X_selected)[0]
            probabilities = [
                {
                    "classe": id_to_filiere.get(
                        int(model.classes_[i]), str(model.classes_[i])
                    ),
                    "probabilite": round(float(proba[i]) * 100, 2),
                }
                for i in range(len(proba))
            ]
            probabilities.sort(key=lambda x: x["probabilite"], reverse=True)

        execution_time = round(time.time() - start_time, 3)
        print(f"🟢 Orientation prédite : {orientation} ({execution_time}s)")

        return {
            "success": True,
            "orientation": orientation,
            "probabilites": probabilities,
            "execution_time": execution_time,
        }

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {str(e)}")