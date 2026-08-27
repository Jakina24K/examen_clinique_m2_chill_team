import pandas as pd


COL_MAPPING = {
    "Q2 — Quel est votre statut actuel ?": "statut",
    "Q3 — Quel est votre âge ?": "age",
    "Q6 — Si vous avez passé le Baccalauréat, dans quelle série ?": "bac_serie",
    "Q9 — Évaluez votre niveau actuel en Mathématiques :": "niveau_mathematiques_general",
    "Q10 — Évaluez votre niveau actuel en Programmation / Informatique :": "niveau_programmation_informatique_general",
    "Q11 — Évaluez votre niveau actuel en Physique :": "niveau_physique_general",
    "Q12 — Évaluez votre niveau actuel en Chimie / Biologie :": "niveau_chimie_biologie_general",
    "Q13 — Parmi les compétences suivantes, lesquelles vous correspondent le mieux ? (Choisissez jusqu'à 5)": "competences",
    "Q17 — Quel type d'environnement de travail recherchez-vous ?": "environnement",
    "Q21 — Dans quel secteur d'activité souhaitez-vous travailler ?": "secteur",
}


CHOICE_MAPPING_STATUT = {
    "Étudiant (actuellement en formation)": 0,
    "Professionnel (en activité)": 1,
    "Étudiant et professionnel (alternance/stage)": 0,
    "Autre": 0,
}


CHOICE_MAPPING_BAC_SERIE = {
    "Série L (Littéraire)": 0,
    "Série C (Mathématiques)": 1,
    "Série D (Sciences Expérimentales)": 2,
    "Série S (Scientifique)": 3,
    "Série OSE (Économique et Social)": 4,
    "Série A1": 5,
    "Série A2": 6,
    "Je n'ai pas passé le Baccalauréat": 0,
    "Autre (précisez)": 0,
}


CHOICE_MAPPING_ENVIRONNEMENT = {
    "Bureau": 0,
    "Terrain / Extérieur": 1,
    "Laboratoire": 2,
    "Télétravail / Distanciel": 3,
    "Mixte (Bureau / Télétravail)": 4,
    "Industrie / Usine": 5,
    "Autre (précisez)": 0,
}


CHOICE_MAPPING_SECTEUR = {
    "Industries / Production": 0,
    "Services / Conseil": 1,
    "Commerce / Distribution": 2,
    "Finance / Assurance": 3,
    "Informatique / Numérique": 4,
    "Télécommunications": 5,
    "Santé / Pharmacie": 6,
    "Éducation / Formation": 7,
    "Construction / BTP": 8,
    "Agriculture / Agroalimentaire": 9,
    "Énergie / Mines": 10,
    "Tourisme / Hôtellerie": 11,
    "Médias / Communication": 12,
    "Droit / Justice": 13,
    "Secteur public / Administration": 14,
    "Autre (précisez)": 0,
}


COMPETENCE_MAPPING = {
    "Résolution de problèmes complexes": "analyse_synthese",
    "Travail en équipe / Collaboration": "travail_equipe",
    "Autonomie / Initiative": "autonomie",
    "Créativité / Innovation": "creativite",
    "Rigueur / Organisation": "analyse_synthese",
    "Communication / Expression orale": None,
    "Analyse / Synthèse": "analyse_synthese",
    "Adaptabilité / Flexibilité": None,
    "Leadership / Gestion d'équipe": "gestion_projet",
    "Négociation / Persuasion": None,
    "Gestion de projet": "gestion_projet",
    "Esprit critique": "analyse_synthese",
    "Méthodologie / Planification": "gestion_projet",
}


# ============================================================
# MAPPING : Colonnes générales → Colonnes spécialisées du dataset
# ============================================================

MATIERE_LEVEL_MAPPING = {
    "niveau_mathematiques_general": [
        "niveau_algèbre",
        "niveau_analyse_mathématique",
        "niveau_mathématique_discrète",
        "niveau_mathématique_financière",
        "niveau_probabilité_statistique",
        "niveau_econométrie",
    ],

    "niveau_programmation_informatique_general": [
        "niveau_algorithme",
        "niveau_langage_c",
        "niveau_base_de_données",
        "niveau_html_css",
        "niveau_informatique_scientifique",
        "niveau_structure_de_données",
        "niveau_structure_des_ordinateurs",
    ],

    "niveau_physique_general": [
        "niveau_physique",
        "niveau_thermodynamique",
        "niveau_electricité",
        "niveau_mécanique",
        "niveau_électromécanique",
        "niveau_thermophysique",
    ],

    "niveau_chimie_biologie_general": [
        "niveau_chimie",
        "niveau_biologie_animale",
        "niveau_biochimie",
        "niveau_biologie_cellulaire",
        "niveau_virologie",
        "niveau_enzymologie",
        "niveau_bactériologie",
        "niveau_physiologie_animale",
        "niveau_génétique",
        "niveau_physiologie_végétale",
        "niveau_agronomie",
        "niveau_zootechnie",
    ],
}


def map_age_to_numeric(age):
    if pd.isna(age):
        return 25

    age = str(age)

    if "Moins de 18 ans" in age:
        return 17
    if "18 - 20 ans" in age:
        return 19
    if "21 - 25 ans" in age:
        return 23
    if "26 - 30 ans" in age:
        return 28
    if "31 - 40 ans" in age:
        return 35
    if "41 - 50 ans" in age:
        return 45
    if "Plus de 50 ans" in age:
        return 55

    try:
        return float(age)
    except Exception:
        return 25


def preprocess_survey_data(
    survey_df: pd.DataFrame,
    model_features: list
) -> pd.DataFrame:

    processed_df = survey_df.copy()

    # ---------------------------------------------------------
    # 1. Supprimer les colonnes inutiles
    # ---------------------------------------------------------

    processed_df = processed_df.drop(
        columns=[
            "Horodateur",
            "Q1 — J'ai lu et compris les informations ci-dessus et j'accepte librement de participer à cette enquête.",
        ],
        errors="ignore",
    )

    # ---------------------------------------------------------
    # 2. Renommer les colonnes
    # ---------------------------------------------------------

    processed_df = processed_df.rename(columns=COL_MAPPING)

    # ---------------------------------------------------------
    # 3. Age
    # ---------------------------------------------------------

    if "age" in processed_df.columns:
        processed_df["age"] = processed_df["age"].apply(
            map_age_to_numeric
        )

    # ---------------------------------------------------------
    # 4. Variables catégorielles
    # ---------------------------------------------------------

    mappings = {
        "statut": CHOICE_MAPPING_STATUT,
        "bac_serie": CHOICE_MAPPING_BAC_SERIE,
        "environnement": CHOICE_MAPPING_ENVIRONNEMENT,
        "secteur": CHOICE_MAPPING_SECTEUR,
    }

    for col, mapping in mappings.items():

        if col in processed_df.columns:

            processed_df[col] = (
                processed_df[col]
                .map(mapping)
                .fillna(0)
                .astype(int)
            )

    # ---------------------------------------------------------
    # 5. Compétences
    # ---------------------------------------------------------

    competence_features = [
        "travail_equipe",
        "autonomie",
        "analyse_synthese",
        "creativite",
        "gestion_projet",
    ]

    for feature in competence_features:
        processed_df[feature] = 0

    if "competences" in processed_df.columns:

        for index, row in processed_df.iterrows():

            value = row["competences"]

            if pd.isna(value):
                continue

            # Google Forms peut utiliser "," ou ";"
            value = str(value).replace(",", ";")

            selected = [
                x.strip()
                for x in value.split(";")
                if x.strip()
            ]

            for competence in selected:

                mapped_feature = COMPETENCE_MAPPING.get(
                    competence
                )

                if mapped_feature:
                    processed_df.loc[
                        index,
                        mapped_feature
                    ] = 1

    processed_df = processed_df.drop(
        columns=["competences"],
        errors="ignore"
    )

    # ---------------------------------------------------------
    # 6. Niveaux des matières (CORRIGÉ)
    # ---------------------------------------------------------
    # Copier les niveaux généraux vers les niveaux spécialisés

    for general_col, specific_cols in MATIERE_LEVEL_MAPPING.items():

        if general_col not in processed_df.columns:
            # Si la colonne générale n'existe pas, utiliser la valeur par défaut (1)
            processed_df[general_col] = 1

        for specific_col in specific_cols:
            # Copier la valeur générale vers chaque colonne spécialisée
            processed_df[specific_col] = processed_df[general_col]

    # ---------------------------------------------------------
    # 7. Supprimer les niveaux généraux
    # ---------------------------------------------------------

    general_level_cols = list(
        MATIERE_LEVEL_MAPPING.keys()
    )

    processed_df = processed_df.drop(
        columns=general_level_cols,
        errors="ignore"
    )

    # ---------------------------------------------------------
    # 8. Ajouter les colonnes qui n'existent pas encore
    #    (domaines supplémentaires non couverts par le formulaire)
    # ---------------------------------------------------------
    # Ces colonnes sont dans le dataset d'entraînement mais 
    # ne sont pas capturées par le formulaire actuel.
    # On les initialise à 1 (valeur neutre)

    other_level_columns = [
    "niveau_anglais",
    "niveau_assainissement",
    "niveau_autocad",
    "niveau_comptabilité",
    "niveau_dessin",
    "niveau_droit",
    "niveau_ecologie",
    "niveau_economie",
    "niveau_electronique",
    "niveau_environnement",
    "niveau_finance_publique",
    "niveau_fiscalité",
    "niveau_français",
    "niveau_géologie",
    "niveau_hydraulique",
    "niveau_hygiène",
    "niveau_industries_pharmaceutiques",
    "niveau_informatique",
    "niveau_logique",
    "niveau_macroéconomie_microéconomie",
    "niveau_maintenance",
    "niveau_marketing",
    "niveau_musique",
    "niveau_nutrition_humaine",
    "niveau_organisation_dentreprise",
    "niveau_ouvrages_métalliques",
    "niveau_pharmacologie",
    "niveau_pétrologie",
    "niveau_science_des_aliments",
    "niveau_sites_touristiques",
    "niveau_statistiques_appliquée",
    "niveau_technique_bancaire",
    "niveau_analyse",
    "niveau_mathématiques",
    "niveau_botanique",
]
    for col in other_level_columns:
        if col not in processed_df.columns:
            processed_df[col] = 1

    # ---------------------------------------------------------
    # 9. Garder uniquement les features du modèle
    # ---------------------------------------------------------

    # S'assurer que toutes les colonnes nécessaires existent
    for feature in model_features:
        if feature not in processed_df.columns:
            processed_df[feature] = 0

    # Sélectionner UNIQUEMENT les colonnes du modèle, dans l'ordre
    processed_df = processed_df[model_features]

    # ---------------------------------------------------------
    # 10. Conversion numérique et remplissage
    # ---------------------------------------------------------

    for col in processed_df.columns:
        processed_df[col] = pd.to_numeric(
            processed_df[col],
            errors="coerce"
        )

    processed_df = processed_df.fillna(0)

    return processed_df