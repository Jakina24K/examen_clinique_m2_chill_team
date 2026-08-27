import numpy as np
import json
from pathlib import Path
import pandas as pd

def generate_response(
    affinity: float,
    rng: np.random.Generator,
    concentration: float = 8.0
) -> int:
    """
    Génère une réponse de 1 à 5 à partir d'une affinité
    comprise entre 0 et 1.

    affinity:
        0.0 = très faible affinité
        1.0 = très forte affinité

    concentration:
        Contrôle la dispersion des réponses.
        Plus elle est élevée, plus les réponses sont
        proches de la tendance centrale.
    """

    # Sécurité
    affinity = np.clip(affinity, 0.0, 1.0)

    # On évite que la moyenne soit exactement 0 ou 1.
    mean = 0.05 + 0.90 * affinity

    # Paramètres de la distribution Beta
    alpha = mean * concentration
    beta = (1 - mean) * concentration

    # Génération d'une valeur entre 0 et 1
    value = rng.beta(alpha, beta)

    # Conversion de [0, 1] vers [1, 5]
    response = 1 + 4 * value

    # Arrondi + sécurité
    return int(np.clip(np.rint(response), 1, 5))



DOMAIN_GROUPS = {
    "informatique": [
        "programmation",
        "algorithmique",
        "bases_donnees",
        "web"
    ],

    "maths_data": [
        "maths_logique",
        "data_statistiques"
    ],

    "gestion": [
        "gestion_organisation",
        "comptabilite_finance",
        "economie",
        "marketing_commerce",
        "droit"
    ],

    "sciences": [
        "physique",
        "chimie",
        "biologie",
        "biotechnologie"
    ],

    "genie": [
        "electronique_hardware",
        "mecanique",
        "construction_conception",
        "industrie_maintenance"
    ],

    "tourisme": [
        "tourisme_environnement"
    ],

    "musique": [
        "musique"
    ]
}

def generate_domain_level(
    affinities,
    features,
    rng,
    individual_variation=0.04
):
    """
    Génère un niveau latent d'intérêt pour un groupe
    de matières.

    Retourne une valeur comprise entre 0 et 1.
    """

    # Moyenne des affinités du parcours
    base_affinity = np.mean([
        affinities[feature]
        for feature in features
    ])

    # Variation personnelle de l'étudiant
    level = base_affinity + rng.normal(
        0,
        individual_variation
    )

    return float(np.clip(level, 0, 1))

def generate_domain_responses(
    domain_level,
    features,
    affinities,
    rng,
    concentration=8.0
):
    """
    Génère les réponses aux différentes features
    d'un même domaine.
    """

    responses = {}

    for feature in features:

        # Différence entre la préférence générale
        # de l'étudiant et l'affinité spécifique
        # de la filière pour cette matière.
        feature_adjustment = (
            affinities[feature]
            - np.mean([
                affinities[f]
                for f in features
            ])
        )

        effective_affinity = (
            domain_level
            + feature_adjustment
        )

        effective_affinity = np.clip(
            effective_affinity,
            0,
            1
        )

        responses[feature] = generate_response(
            effective_affinity,
            rng,
            concentration
        )

    return responses

def load_affinity_matrix():
    """
    Charge la matrice d'affinité depuis le fichier JSON.
    """

    config_path = (
        Path(__file__).parent.parent
        / "config"
        / "affinity_matrix.json"
    )

    with open(config_path, "r", encoding="utf-8") as file:
        return json.load(file)
    
def generate_student(
    parcours: str,
    affinity_matrix: dict,
    rng: np.random.Generator
) -> dict:

    if parcours not in affinity_matrix:
        raise ValueError(
            f"Parcours inconnu : {parcours}"
        )

    affinities = affinity_matrix[parcours]

    student = {}

    # Génération domaine par domaine
    for domain, features in DOMAIN_GROUPS.items():

        # Vérifie que les features existent
        valid_features = [
            feature
            for feature in features
            if feature in affinities
        ]

        if not valid_features:
            continue

        # Niveau latent du domaine
        domain_level = generate_domain_level(
            affinities,
            valid_features,
            rng
        )

        # Génération des réponses
        responses = generate_domain_responses(
            domain_level,
            valid_features,
            affinities,
            rng
        )

        student.update(responses)

    # Classe cible
    student["parcours"] = parcours

    return student

def generate_dataset(
        affinity_matrix: dict,
        students_per_class: int,
        seed: int = 42
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    rows = []

    for parcours in affinity_matrix:

        for _ in range(students_per_class):

            student = generate_student(
                parcours=parcours,
                affinity_matrix=affinity_matrix,
                rng=rng
            )

            rows.append(student)

    return pd.DataFrame(rows)

if __name__ == "__main__":

    rng = np.random.default_rng(42)

    affinity_matrix = load_affinity_matrix()

    student = generate_student(
        parcours="ISAIA",
        affinity_matrix=affinity_matrix,
        rng=rng
    )

    print("Étudiant généré :")
    print()

    for feature, value in student.items():
        print(f"{feature:25} : {value}")