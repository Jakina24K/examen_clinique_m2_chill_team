import re
from typing import Tuple, List

# Mots-clés / Patterns à risque d'injection ou d'actions ultra-sensibles
SECURITY_PATTERNS = [
    r"ignore previous instructions",
    r"bypass guardrails",
    r"supprimer la base",
    r"format disk",
    r"drop table",
    r"sudo rm",
    r"change password for admin",
    r"donne-moi accès admin"
]

SENITIVE_CATEGORIES_KEYWORDS = {
    "Cybersécurité": ["phishing", "piraté", "compromis", "malware", "virus", "ransomware"],
    "Droits d'accès": ["privilège", "admin", "mot de passe d'un tiers", "droit d'accès"]
}


def evaluate_security(description: str) -> Tuple[bool, str, List[str]]:
    """
    Évalue le ticket contre les attaques (Prompt Injection) et identifie les actions sensibles.
    Retourne: (validation_humaine_requise, raison, avertissements)
    """
    desc_lower = description.lower()
    warnings = []

    # 1. Détection de Prompt Injection ou tentatives malveillantes
    for pattern in SECURITY_PATTERNS:
        if re.search(pattern, desc_lower):
            return True, f"Alerte de sécurité : Tentative d'injection ou instruction malveillante détectée ('{pattern}').", warnings

    # 2. Détection d'opérations sensibles nécessitant validation humaine (Scénario 4)
    for category, keywords in SENITIVE_CATEGORIES_KEYWORDS.items():
        for kw in keywords:
            if kw in desc_lower:
                warnings.append(f"Mot-clé sensible détecté : {kw}")
                return True, f"Demande sensible relative à la {category}. Validation humaine requise avant toute modification.", warnings

    return False, "", warnings