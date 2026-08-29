import json
import logging
from datetime import datetime, timezone
from pathlib import Path

LOG_FILE = Path("logs/orientation.log")
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


def log_response(response_data: dict, log_file: Path = LOG_FILE) -> None:
    """
    Log une réponse JSON structurée (rag / ontology / ml) dans un fichier.
    Écrit à la fois un résumé lisible et l'entrée brute en JSON Lines.
    """
    timestamp = datetime.now(timezone.utc).isoformat()

    rag = response_data.get("rag", {})
    ontology = response_data.get("ontology", {})
    ml = response_data.get("ml", {})

    # Détection d'erreurs/avertissements dans le module RAG
    warnings = rag.get("avertissements", [])
    has_error = bool(warnings) or rag.get("incertitude", "").lower().startswith("élevée")

    level = "ERROR" if has_error else "INFO"

    # --- Résumé structuré ---
    summary = {
        "timestamp": timestamp,
        "level": level,
        "rag": {
            "reponse": rag.get("reponse"),
            "incertitude": rag.get("incertitude"),
            "temps_execution_s": rag.get("temps_execution_s"),
            "nb_avertissements": len(warnings),
            "avertissements": warnings,
        },
        "ontology": {
            "competences": ontology.get("profil_extrait", {}).get("competences", []),
            "centres_interet": ontology.get("profil_extrait", {}).get("centres_interet", []),
            "formation_demandee": ontology.get("formation_demandee"),
            "eligible": ontology.get("eligible"),
        },
        "ml": {
            "success": ml.get("success"),
            "orientation": ml.get("orientation"),
            "top_probabilite": (
                ml.get("probabilites", [{}])[0]
                if ml.get("probabilites") else None
            ),
            "execution_time": ml.get("execution_time"),
        },
    }

    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(summary, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"[LOGGING ERROR] Impossible d'écrire le log : {e}")