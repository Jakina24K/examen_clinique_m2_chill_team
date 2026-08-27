"""
app/evaluation/eval_rag.py
-----------------------------
BONUS — Harnais d'évaluation minimal pour la recherche documentaire.

Le sujet exige un jeu d'au moins 32 cas répartis en 8 catégories (factuel,
comparaison, ML, multi-étapes, hors-corpus, ambigu, injection, biais...).
Ce script ne couvre que la brique RAG ("pertinence des documents récupérés",
"rappel des sources utiles") ; dupliquez ce pattern pour évaluer l'agent et
le modèle ML de bout en bout.

Format attendu d'un cas : {"question": str, "doc_id_attendu": str}
-> le doc_id_attendu doit correspondre à un chunk_id retourné par ingest.py
   (loggez les chunk_id pendant l'ingestion pour construire ce jeu).

Exécution : python -m app.evaluation.eval_rag
"""

import json
import logging
from pathlib import Path
from typing import List, Dict

from app.rag.retriever import search_knowledge_base

logging.basicConfig(level=logging.INFO, format="%(asctime)s [EVAL] %(message)s")
logger = logging.getLogger(__name__)

EVAL_SET_PATH = Path("data/eval/rag_eval_set.json")
TOP_K = 4


def load_eval_set(path: Path = EVAL_SET_PATH) -> List[Dict]:
    if not path.exists():
        logger.warning(f"Jeu d'évaluation introuvable : {path}. Créez-le (voir docstring).")
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate(eval_set: List[Dict], top_k: int = TOP_K) -> Dict:
    hits, reciprocal_ranks, latences = 0, [], []
    import time

    for case in eval_set:
        t0 = time.time()
        results = search_knowledge_base(case["question"], top_k=top_k)
        latences.append(time.time() - t0)

        retrieved_ids = [r.doc_id for r in results]
        if case["doc_id_attendu"] in retrieved_ids:
            hits += 1
            rank = retrieved_ids.index(case["doc_id_attendu"]) + 1
            reciprocal_ranks.append(1 / rank)
        else:
            reciprocal_ranks.append(0.0)

    n = max(len(eval_set), 1)
    return {
        "n_cas": len(eval_set),
        "recall_at_k": round(hits / n, 3),
        "mrr": round(sum(reciprocal_ranks) / n, 3),
        "latence_moyenne_s": round(sum(latences) / n, 3) if latences else 0.0,
    }


if __name__ == "__main__":
    eval_set = load_eval_set()
    if eval_set:
        report = evaluate(eval_set)
        logger.info(f"Résultats RAG : {json.dumps(report, indent=2, ensure_ascii=False)}")