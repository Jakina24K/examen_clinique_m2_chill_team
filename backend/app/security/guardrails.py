"""
app/security/guardrails.py
-----------------------------
Garde-fous de pré-traitement pour ORIENT'IA (exécutés AVANT tout appel LLM).

Couvre la section "Risques à prendre en charge" du sujet :
  - injections de prompt / instructions malveillantes
  - invention de formations ou de règles d'admission inexistantes
  - profilage psychologique / inférence de traits de personnalité à partir
    du style d'écriture (explicitement interdit : "aucune validité établie")
  - recommandations fondées sur des critères discriminatoires (sexe, âge...)

Ces règles sont volontairement déterministes (regex) : rapides, gratuites,
et non contournables par un prompt utilisateur habile — contrairement à une
simple instruction "sois prudent" donnée au LLM.
"""

import re
from typing import List, Tuple

# --- 1. Injection de prompt / instructions malveillantes ---
PROMPT_INJECTION_PATTERNS = [
    r"ignore (les|tes|toutes les) (instructions|documents|règles)",
    r"oublie (tes|les) (règles|consignes|instructions)",
    r"bypass|contourne (le|les) garde-?fou",
    r"agis comme si",
    r"tu n'es plus orient'?ia",
    r"sans (restriction|filtre|censure)",
    r"réponds? sans (règle|filtre)",
    r"mode (développeur|debug|admin)",
]

# --- 2. Invention de formations / affirmations non justifiées ---
FABRICATION_PATTERNS = [
    r"invente (une|un) (formation|parcours|filière|diplôme)",
    r"affirme qu'(une|un) (nouvelle )?(formation|parcours|filière) (existe|est disponible)",
    r"fais comme si .* (existait|était officiel)",
    r"suppose qu'il existe",
]

# --- 3. Profilage psychologique / inférence de traits de personnalité ---
PSYCH_PROFILING_PATTERNS = [
    r"analyse (ma|mon) personnalité",
    r"quel(le)? est mon profil psychologique",
    r"d'après (mon|ma) (style d'écriture|façon d'écrire|manière de parler)",
    r"dis-moi qui je suis (vraiment)?",
    r"quel type de personnalité (ai-je|as-tu détecté)",
    r"analyse (mes|mon) traits de caractère",
]

# --- 4. Critères discriminatoires interdits comme base de recommandation ---
DISCRIMINATORY_PATTERNS = [
    r"recommande .* uniquement (à partir|en fonction) du sexe",
    r"recommande .* uniquement (à partir|en fonction) de l'âge",
    r"selon (son|sa) (origine|religion|orientation sexuelle)",
    r"parce qu'(il|elle) est (une femme|un homme|trop (jeune|vieux))",
]


def _match_any(patterns: List[str], text: str) -> str:
    for p in patterns:
        if re.search(p, text):
            return p
    return ""


def evaluate_security(description: str) -> Tuple[bool, str, List[str]]:
    """
    Évalue un message utilisateur avant tout traitement par l'agent.
    Retourne : (bloque: bool, raison: str, avertissements: list[str])
    """
    text = description.lower().strip()
    text = text.replace("\u2019", "'")
    warnings: List[str] = []

    if _match_any(PROMPT_INJECTION_PATTERNS, text):
        return True, (
            "Tentative détectée de contournement des instructions du système "
            "(injection de prompt)."
        ), warnings

    if _match_any(FABRICATION_PATTERNS, text):
        return True, (
            "ORIENT'IA ne peut ni inventer de formation ni affirmer l'existence "
            "d'un parcours non présent dans le corpus officiel."
        ), warnings

    if _match_any(PSYCH_PROFILING_PATTERNS, text):
        return True, (
            "ORIENT'IA n'effectue aucun profilage psychologique ni inférence de "
            "traits de personnalité à partir du style d'écriture : une telle "
            "inférence n'a aucune validité établie et ne peut fonder une "
            "recommandation d'orientation."
        ), warnings

    if _match_any(DISCRIMINATORY_PATTERNS, text):
        return True, (
            "ORIENT'IA ne fonde ses recommandations sur aucune caractéristique "
            "personnelle sensible (sexe, âge, origine...) sans justification "
            "pédagogique légitime."
        ), warnings

    # Avertissement doux (non bloquant) : demande d'information personnelle
    if re.search(r"(numéro de téléphone|adresse personnelle|carte d'identité)", text):
        warnings.append("Demande d'information personnelle détectée - à traiter avec prudence.")

    return False, "", warnings