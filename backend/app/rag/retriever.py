"""
app/rag/retriever.py
---------------------
Recherche vectorielle dans ChromaDB avec scores de pertinence exposés.

Le sujet ORIENT'IA exige explicitement des traces incluant "les passages
récupérés" et "les scores de recherche" (section Observabilité) : ce module
retourne donc toujours le score, jamais seulement le texte brut.
"""

import os
import logging
from dataclasses import dataclass, asdict
from typing import List, Optional

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from app.core.config import settings

# Transmet le token du .env à l'environnement système pour Hugging Face
if settings.HF_TOKEN:
    os.environ["HF_TOKEN"] = settings.HF_TOKEN

logger = logging.getLogger(__name__)

PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
COLLECTION_NAME = "orientia_knowledge"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Seuil sous lequel un résultat est jugé non pertinent. À calibrer sur votre jeu
# d'évaluation (voir app/evaluation/eval_rag.py) plutôt que laissé arbitraire.
RELEVANCE_THRESHOLD = 0.35

_embeddings = None
_vectorstore = None


@dataclass
class SourceRAG:
    """Contrat de sortie consommé par l'agent et affiché comme citation."""
    doc_id: str
    titre: str
    source_file: str
    score_pertinence: float
    extrait: str

    def to_dict(self):
        return asdict(self)


def _get_vectorstore() -> Chroma:
    global _embeddings, _vectorstore
    if _vectorstore is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        _vectorstore = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=_embeddings,
            persist_directory=PERSIST_DIR,
            collection_metadata={"hnsw:space": "cosine"},
        )
        # Déplacé ICI (à l'intérieur du if) :
        count = _vectorstore._collection.count()
        if count == 0:
            logger.warning(f"⚠️  Collection '{COLLECTION_NAME}' est VIDE — avez-vous lancé `python -m app.rag.ingest` ?")
        else:
            logger.info(f"Collection '{COLLECTION_NAME}' chargée : {count} chunks disponibles.")
    
    return _vectorstore


def search_knowledge_base(
    query: str,
    top_k: int = 4,
    min_score: Optional[float] = None,
) -> List[SourceRAG]:
    """
    Recherche les top_k chunks les plus pertinents pour `query`.

    Retourne une liste vide (jamais une exception) si la base est vide ou
    absente : cela permet à l'agent de dire explicitement "information
    absente du corpus" plutôt que de planter ou d'halluciner.
    """
    try:
        vectorstore = _get_vectorstore()
    except Exception as e:
        logger.error(f"Base vectorielle inaccessible : {e}")
        return []

    try:
        # Score normalisé 0-1 (0 = pas pertinent, 1 = pertinent) : plus interprétable
        # qu'une distance brute, et directement citable dans la réponse finale.
        results = vectorstore.similarity_search_with_relevance_scores(query, k=top_k)
    except Exception as e:
        logger.error(f"Erreur pendant la recherche RAG : {e}")
        return []

    threshold = min_score if min_score is not None else RELEVANCE_THRESHOLD
    sources: List[SourceRAG] = []
    for doc, score in results:
        if score < threshold:
            logger.info(f"Chunk écarté (score={score:.2f} < seuil={threshold})")
            continue
        sources.append(
            SourceRAG(
                doc_id=doc.metadata.get("chunk_id", "unknown"),
                titre=doc.metadata.get("titre", "Document"),
                source_file=doc.metadata.get("source_file", "inconnu"),
                score_pertinence=round(min(1.0, max(0.0, float(score))), 3),
                extrait=doc.page_content.strip(),
            )
        )

    logger.info(f"Requête='{query[:60]}...' -> {len(sources)}/{len(results)} chunks retenus")
    return sources