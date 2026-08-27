"""
app/tools/tools.py
--------------------
Outils callables par l'agent LangChain. Chaque outil réalise une opération
technique identifiable (pas une simple instruction de prompt), conformément
à la section "Outils" du sujet ORIENT'IA.

3 paradigmes distincts, orchestrés ensuite par le LLM dans agent.py :
  1. rechercher_formation  -> RAG          (probabiliste, dense retrieval)
  2. analyser_profil_ml    -> Machine Learning (probabiliste, classifieur)
  3. verifier_prerequis    -> IA Symbolique (déterministe, règles/graphe)
"""

import logging
from typing import List, Dict, Any, Optional

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from app.rag.retriever import search_knowledge_base

logger = logging.getLogger(__name__)

# ==========================================================================
# OUTIL 1 — RAG : rechercher_formation
# ==========================================================================

class RechercherFormationInput(BaseModel):
    query: str = Field(..., description="Question ou sujet de formation à rechercher (ex: 'prérequis IGGLIA')")
    top_k: int = Field(4, description="Nombre de passages à retourner")


@tool("rechercher_formation", args_schema=RechercherFormationInput)
def rechercher_formation(query: str, top_k: int = 4) -> List[Dict[str, Any]]:
    """
    Recherche documentaire (RAG) dans le corpus pédagogique ISPM.
    À utiliser pour toute question factuelle sur une formation, un parcours,
    des prérequis textuels décrits en langage naturel, ou des débouchés
    mentionnés dans les sources officielles. Retourne une liste de passages
    avec score de pertinence et fichier source — nécessaire pour citer les
    sources dans la réponse finale.
    """
    sources = search_knowledge_base(query, top_k=top_k)
    if not sources:
        logger.info(f"rechercher_formation: aucun résultat pertinent pour '{query}'")
        return []
    return [s.to_dict() for s in sources]


# ==========================================================================
# OUTIL 2 — Machine Learning : analyser_profil_ml
# ==========================================================================

class ProfilInput(BaseModel):
    matieres_preferees: List[str] = Field(default_factory=list, description="Matières explicitement déclarées par l'étudiant")
    competences: List[str] = Field(default_factory=list, description="Compétences explicitement déclarées")
    centres_interet: List[str] = Field(default_factory=list, description="Centres d'intérêt explicitement déclarés")


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

    TODO hackathon : remplacer ce mock par le vrai classifieur entraîné, ex.
        model = joblib.load("models/orientation_clf.pkl")
        vect = vectorizer.transform([features])
        proba = model.predict_proba(vect)
    """
    matieres_preferees = matieres_preferees or []
    competences = competences or []
    centres_interet = centres_interet or []

    if not (matieres_preferees or competences or centres_interet):
        return {
            "statut": "profil_insuffisant",
            "message": "Profil trop incomplet pour une prédiction fiable — poser une question de clarification.",
            "predictions": [],
        }

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

    return {
        "statut": "ok",
        "modele": "mock_heuristique_v0 (à remplacer par le classifieur entraîné)",
        "predictions": predictions,
        "indice_confiance": round(confiance, 3),
        "features_utilisees": {
            "matieres_preferees": matieres_preferees,
            "competences": competences,
            "centres_interet": centres_interet,
        },
    }


# ==========================================================================
# OUTIL 3 — IA Symbolique : verifier_prerequis
# ==========================================================================

# Mini ontologie / graphe de connaissances en mémoire (Parcours -[necessite]-> Prerequis).
# À terme : remplacer par un vrai graphe (networkx / RDF) chargé depuis data/knowledge/,
# ce qui permettrait un raisonnement multi-étape (Parcours -> Matiere -> Competence).
ONTOLOGIE_PREREQUIS: Dict[str, List[str]] = {
    "ISAIA": ["mathématiques niveau L2", "bases en programmation", "algèbre linéaire"],
    "IGGLIA": ["bases en programmation", "structures de données"],
    "Réseaux & Cybersécurité": ["réseaux informatiques de base", "systèmes d'exploitation"],
}


class VerifierPrerequisInput(BaseModel):
    formation: str = Field(..., description="Nom du parcours/formation (ex: 'ISAIA')")
    competences: List[str] = Field(..., description="Compétences que l'étudiant déclare posséder")


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
        return {
            "statut": "formation_inconnue",
            "message": (
                f"'{formation}' n'existe pas dans l'ontologie ORIENT'IA. "
                f"Ne pas inventer de parcours : orienter l'utilisateur vers l'administration."
            ),
            "formations_connues": list(ONTOLOGIE_PREREQUIS.keys()),
        }

    requis = ONTOLOGIE_PREREQUIS[formation_key]
    possedees = {c.strip().lower() for c in competences}
    manquants = [r for r in requis if r.lower() not in possedees]

    return {
        "statut": "ok",
        "formation": formation_key,
        "prerequis_requis": requis,
        "prerequis_manquants": manquants,
        "eligible": len(manquants) == 0,
        "raisonnement": (
            f"{len(requis) - len(manquants)}/{len(requis)} prérequis satisfaits "
            f"(règle déterministe, indépendante du LLM)."
        ),
    }


AVAILABLE_TOOLS = [rechercher_formation, analyser_profil_ml, verifier_prerequis]