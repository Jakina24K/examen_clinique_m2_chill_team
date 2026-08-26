"""
Générateur de profils étudiants synthétiques — ORIENT'IA (ISPM)
==================================================================

Objectif
--------
Produire un jeu de données d'ENTRAINEMENT pour le modèle de score d'adéquation
profil -> parcours. Ce jeu est volontairement imparfait :
  - bruit sur les features (un profil "type info" n'a pas TOUJOURS toutes les
    features info) ;
  - profils frontière / ambigus entre deux domaines proches ;
  - une fraction de "mauvais choix" (l'étiquette ne colle pas parfaitement au
    profil), pour imiter le fait que dans la vraie vie, le parcours choisi
    n'est pas toujours celui qui correspond le mieux au profil ;
  - valeurs manquantes sur certains champs (profil incomplet, comme dans une
    vraie collecte progressive par l'agent) ;
  - dispersion réaliste des résultats scolaires.

Rappel du sujet : ce jeu sert à l'ENTRAINEMENT uniquement. La VALIDATION et
le TEST doivent se faire sur les réponses de l'enquête réelle (étudiants +
professionnels), afin de mesurer la capacité de généralisation
synthétique -> réel.

À documenter dans le rapport (section "Traçabilité") :
  - méthode de génération : voir ce script (les probabilités par domaine
    ci-dessous sont FIXÉES À DIRE D'EXPERT, pas mesurées -> c'est une
    hypothèse forte à assumer explicitement) ;
  - hypothèses : indépendance approximative entre les features au sein d'un
    domaine, bruit gaussien sur les résultats scolaires ;
  - biais introduits : sur-représentation volontaire du domaine informatique
    (4 parcours sur ~14) si tirage uniforme par parcours -> corrigé ici par
    un tirage uniforme par DOMAINE puis par parcours dans le domaine ;
  - contrôles de cohérence : voir la fonction `sanity_checks`.
"""

import csv
import random
from dataclasses import dataclass, field

random.seed(42)  # reproductibilité -> à mentionner dans le registre

# ---------------------------------------------------------------------------
# 1. Référentiel parcours / domaines (dérivé de filieres_a_l_ispm.txt)
# ---------------------------------------------------------------------------

DOMAINES = {
    "informatique": ["IGGLIA", "IMTICIA", "ESIIA", "ISAIA"],
    "biotechnologies": ["IAA", "AEE", "PIP"],
    "gestion_finance": ["CAA", "DTJA", "EMP", "FIC"],
    "tourisme_environnement": ["TEH"],
    "industrie_btp": ["EMII", "GCA", "ICMP"],
}

# Vocabulaire "profil candidat" (distinct du vocabulaire matières-ISPM,
# cf. discussion : un candidat déclare des affinités larges, pas les
# intitulés précis des UE).
MATIERES = [
    "maths", "physique", "info_algo", "biologie", "chimie",
    "economie_gestion", "droit", "technique_manuel", "langues",
    "tourisme", "arts",
]
COMPETENCES = [
    "programmation", "analyse_quantitative", "communication",
    "gestion_projet", "manuel_technique", "creativite",
]
CENTRES_INTERET = [
    "recherche", "entrepreneuriat", "terrain", "donnees_finance",
    "sante_bio", "industrie",
]
ENVIRONNEMENTS = ["bureau", "laboratoire", "terrain", "atelier", "mixte"]

# ---------------------------------------------------------------------------
# 2. Profil-type ("affinité") par domaine — HYPOTHÈSE À DIRE D'EXPERT
#    Chaque valeur = probabilité qu'un candidat "typique" de ce domaine
#    coche cet item. Ce sont des choix arbitraires raisonnables, PAS des
#    données mesurées : à assumer comme limite dans le rapport.
# ---------------------------------------------------------------------------

AFFINITE_DOMAINE = {
    "informatique": {
        "matieres": {"maths": .8, "physique": .5, "info_algo": .9, "biologie": .05,
                      "chimie": .05, "economie_gestion": .2, "droit": .05,
                      "technique_manuel": .1, "langues": .3, "tourisme": .02, "arts": .1},
        "competences": {"programmation": .85, "analyse_quantitative": .6,
                         "communication": .3, "gestion_projet": .3,
                         "manuel_technique": .1, "creativite": .3},
        "interets": {"recherche": .4, "entrepreneuriat": .35, "terrain": .1,
                      "donnees_finance": .3, "sante_bio": .05, "industrie": .2},
        "environnement": {"bureau": .5, "laboratoire": .15, "terrain": .05,
                           "atelier": .1, "mixte": .2},
        "moyenne": (11, 16),  # (min, max) plage réaliste pour tirage bruité
    },
    "biotechnologies": {
        "matieres": {"maths": .3, "physique": .3, "info_algo": .15, "biologie": .9,
                      "chimie": .8, "economie_gestion": .1, "droit": .05,
                      "technique_manuel": .15, "langues": .2, "tourisme": .05, "arts": .05},
        "competences": {"programmation": .1, "analyse_quantitative": .4,
                         "communication": .3, "gestion_projet": .2,
                         "manuel_technique": .3, "creativite": .2},
        "interets": {"recherche": .6, "entrepreneuriat": .15, "terrain": .3,
                      "donnees_finance": .05, "sante_bio": .8, "industrie": .25},
        "environnement": {"bureau": .1, "laboratoire": .7, "terrain": .1,
                           "atelier": .05, "mixte": .05},
        "moyenne": (10, 16),
    },
    "gestion_finance": {
        "matieres": {"maths": .4, "physique": .1, "info_algo": .15, "biologie": .02,
                      "chimie": .02, "economie_gestion": .9, "droit": .55,
                      "technique_manuel": .05, "langues": .3, "tourisme": .1, "arts": .05},
        "competences": {"programmation": .1, "analyse_quantitative": .5,
                         "communication": .6, "gestion_projet": .55,
                         "manuel_technique": .05, "creativite": .2},
        "interets": {"recherche": .1, "entrepreneuriat": .55, "terrain": .1,
                      "donnees_finance": .7, "sante_bio": .02, "industrie": .1},
        "environnement": {"bureau": .7, "laboratoire": .02, "terrain": .05,
                           "atelier": .02, "mixte": .21},
        "moyenne": (10, 15),
    },
    "tourisme_environnement": {
        "matieres": {"maths": .1, "physique": .05, "info_algo": .05, "biologie": .2,
                      "chimie": .05, "economie_gestion": .3, "droit": .1,
                      "technique_manuel": .1, "langues": .4, "tourisme": .9, "arts": .2},
        "competences": {"programmation": .02, "analyse_quantitative": .2,
                         "communication": .6, "gestion_projet": .35,
                         "manuel_technique": .15, "creativite": .3},
        "interets": {"recherche": .15, "entrepreneuriat": .3, "terrain": .6,
                      "donnees_finance": .1, "sante_bio": .2, "industrie": .05},
        "environnement": {"bureau": .2, "laboratoire": .05, "terrain": .5,
                           "atelier": .05, "mixte": .2},
        "moyenne": (10, 15),
    },
    "industrie_btp": {
        "matieres": {"maths": .5, "physique": .7, "info_algo": .15, "biologie": .02,
                      "chimie": .2, "economie_gestion": .1, "droit": .05,
                      "technique_manuel": .8, "langues": .1, "tourisme": .02, "arts": .1},
        "competences": {"programmation": .1, "analyse_quantitative": .35,
                         "communication": .2, "gestion_projet": .3,
                         "manuel_technique": .8, "creativite": .25},
        "interets": {"recherche": .15, "entrepreneuriat": .2, "terrain": .5,
                      "donnees_finance": .05, "sante_bio": .02, "industrie": .75},
        "environnement": {"bureau": .1, "laboratoire": .1, "terrain": .3,
                           "atelier": .45, "mixte": .05},
        "moyenne": (9, 15),
    },
}

PARCOURS_TO_DOMAINE = {p: d for d, ps in DOMAINES.items() for p in ps}

# ---------------------------------------------------------------------------
# 3. Paramètres de bruit / réalisme (à ajuster et à justifier dans le rapport)
# ---------------------------------------------------------------------------

TAUX_PROFIL_FRONTIERE = 0.15   # profils qui empruntent à 2 domaines proches
TAUX_MAUVAIS_CHOIX = 0.10      # étiquette "parcours choisi" qui ne colle pas
                                # au profil (choix réel imparfait, cf. sujet)
TAUX_VALEUR_MANQUANTE = 0.08   # par champ, simulateur de profil incomplet
BRUIT_MOYENNE = 1.2            # écart-type additionnel sur la moyenne scolaire

DOMAINES_PROCHES = {
    "informatique": ["gestion_finance"],
    "gestion_finance": ["informatique", "tourisme_environnement"],
    "biotechnologies": ["industrie_btp"],
    "tourisme_environnement": ["gestion_finance"],
    "industrie_btp": ["biotechnologies"],
}


def tirer_multi_hot(proba_dict):
    return {k: (1 if random.random() < p else 0) for k, p in proba_dict.items()}


def melanger_deux_domaines(d1, d2, poids_d1=0.6):
    """Mélange les probabilités d'affinité de deux domaines (profil frontière)."""
    out = {}
    for cle in ("matieres", "competences", "interets", "environnement"):
        fusion = {}
        keys = AFFINITE_DOMAINE[d1][cle].keys()
        for k in keys:
            p1 = AFFINITE_DOMAINE[d1][cle][k]
            p2 = AFFINITE_DOMAINE[d2][cle][k]
            fusion[k] = poids_d1 * p1 + (1 - poids_d1) * p2
        out[cle] = fusion
    return out


def appliquer_valeurs_manquantes(profil, champs):
    for champ in champs:
        if random.random() < TAUX_VALEUR_MANQUANTE:
            profil[champ] = None
    return profil


def generer_un_profil(domaine_vise):
    """Génère un profil candidat pour un domaine visé, avec bruit et,
    éventuellement, un mélange frontière et/ou un mauvais choix final."""

    frontiere = random.random() < TAUX_PROFIL_FRONTIERE
    if frontiere and domaine_vise in DOMAINES_PROCHES:
        domaine_proche = random.choice(DOMAINES_PROCHES[domaine_vise])
        affinite = melanger_deux_domaines(domaine_vise, domaine_proche, poids_d1=0.6)
    else:
        affinite = AFFINITE_DOMAINE[domaine_vise]

    matieres = tirer_multi_hot(affinite["matieres"])
    competences = tirer_multi_hot(affinite["competences"])
    interets = tirer_multi_hot(affinite["interets"])
    env_probas = affinite["environnement"]
    environnement = random.choices(list(env_probas.keys()),
                                    weights=list(env_probas.values()), k=1)[0]

    lo, hi = AFFINITE_DOMAINE[domaine_vise]["moyenne"]
    moyenne = random.uniform(lo, hi) + random.gauss(0, BRUIT_MOYENNE)
    moyenne = round(min(18, max(6, moyenne)), 2)

    # Étiquette réellement retenue : le parcours choisi dans le domaine visé,
    # SAUF si on simule un "mauvais choix" (choix réel qui ne suit pas
    # l'affinité du profil -> réalisme des vraies données de choix).
    if random.random() < TAUX_MAUVAIS_CHOIX:
        domaine_final = random.choice([d for d in DOMAINES if d != domaine_vise])
    else:
        domaine_final = domaine_vise
    parcours = random.choice(DOMAINES[domaine_final])

    profil = {
        **{f"matiere__{k}": v for k, v in matieres.items()},
        **{f"competence__{k}": v for k, v in competences.items()},
        **{f"interet__{k}": v for k, v in interets.items()},
        "environnement_souhaite": environnement,
        "moyenne_generale": moyenne,
        "domaine": domaine_final,
        "parcours": parcours,
        "profil_frontiere": int(frontiere),  # utile pour l'analyse d'erreurs, PAS une feature d'entraînement
    }

    champs_optionnels = (
        [f"matiere__{m}" for m in MATIERES]
        + [f"competence__{c}" for c in COMPETENCES]
        + [f"interet__{i}" for i in CENTRES_INTERET]
    )
    profil = appliquer_valeurs_manquantes(profil, champs_optionnels)
    return profil


def generer_dataset(n_par_domaine=120):
    """Tirage UNIFORME PAR DOMAINE (pas par parcours) pour éviter de
    sur-représenter l'informatique (4 parcours) au détriment de parcours
    isolés comme TEH (1 seul parcours). C'est un choix de correction de
    biais explicite -> à documenter."""
    lignes = []
    for domaine in DOMAINES:
        for _ in range(n_par_domaine):
            lignes.append(generer_un_profil(domaine))
    random.shuffle(lignes)
    return lignes


def sanity_checks(lignes):
    """Contrôles de cohérence minimaux avant livraison du jeu de données."""
    erreurs = []
    parcours_valides = set(PARCOURS_TO_DOMAINE.keys())
    for i, ligne in enumerate(lignes):
        if ligne["parcours"] not in parcours_valides:
            erreurs.append(f"ligne {i}: parcours inconnu {ligne['parcours']}")
        if not (6 <= ligne["moyenne_generale"] <= 18):
            erreurs.append(f"ligne {i}: moyenne hors bornes {ligne['moyenne_generale']}")
        if PARCOURS_TO_DOMAINE[ligne["parcours"]] != ligne["domaine"]:
            erreurs.append(f"ligne {i}: incohérence domaine/parcours")
    return erreurs


def repartition_par_parcours(lignes):
    compte = {}
    for l in lignes:
        compte[l["parcours"]] = compte.get(l["parcours"], 0) + 1
    return dict(sorted(compte.items(), key=lambda x: -x[1]))


if __name__ == "__main__":
    dataset = generer_dataset(n_par_domaine=120)  # ~600 profils

    erreurs = sanity_checks(dataset)
    if erreurs:
        print(f"/!\\ {len(erreurs)} incohérences détectées :")
        for e in erreurs[:10]:
            print("  -", e)
        raise SystemExit("Corriger avant livraison.")

    fieldnames = list(dataset[0].keys())
    out_path = "synthetic_profiles.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(dataset)

    print(f"{len(dataset)} profils générés -> {out_path}")
    print("\nRépartition par parcours :")
    for parcours, n in repartition_par_parcours(dataset).items():
        print(f"  {parcours:8s} ({PARCOURS_TO_DOMAINE[parcours]:24s}) : {n}")
    print(f"\nProfils frontière : {sum(l['profil_frontiere'] for l in dataset)} "
          f"({sum(l['profil_frontiere'] for l in dataset)/len(dataset):.1%})")
