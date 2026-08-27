"""
app/rag/ingest.py
------------------
Pipeline d'ingestion RAG pour ORIENT'IA.

Rôle :
    - Charger les documents pédagogiques (PDF + Markdown + TXT) depuis data/knowledge/
    - Les découper en chunks avec chevauchement (contexte préservé)
    - Générer des embeddings 100% locaux (HuggingFace all-MiniLM-L6-v2 -> rapide,
      pas d'appel API, pas de coût, fonctionne hors-ligne pendant le hackathon)
    - Persister dans ChromaDB avec métadonnées traçables (registre de sources)

Dépendances :
    pip install langchain langchain-community langchain-huggingface langchain-chroma \
                sentence-transformers pypdf unstructured chromadb

Exécution : python -m app.rag.ingest
"""

import os
import hashlib
import logging
from pathlib import Path
from typing import List

from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredMarkdownLoader,
    TextLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

logging.basicConfig(level=logging.INFO, format="%(asctime)s [INGEST] %(message)s")
logger = logging.getLogger(__name__)

KNOWLEDGE_DIR = Path(os.getenv("KNOWLEDGE_DIR", "data/knowledge"))
PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
COLLECTION_NAME = "orientia_knowledge"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Chunking : 800 caractères ~= 150-200 tokens, suffisant pour une fiche formation
# sans être trop large pour du reranking. 120 chars d'overlap pour ne pas couper
# une phrase de prérequis pile au milieu.
CHUNK_SIZE = 800
CHUNK_OVERLAP = 120

LOADER_MAP = {
    ".pdf": PyPDFLoader,
    ".md": UnstructuredMarkdownLoader,
    ".txt": TextLoader,
}


def _doc_id(source_path: str, chunk_index: int) -> str:
    """ID stable et déterministe -> nécessaire pour le registre de sources / traçabilité."""
    raw = f"{source_path}-{chunk_index}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]


def load_documents(knowledge_dir: Path = KNOWLEDGE_DIR) -> List[Document]:
    """Charge récursivement tous les fichiers supportés depuis data/knowledge/."""
    docs: List[Document] = []
    if not knowledge_dir.exists():
        logger.warning(f"Répertoire introuvable : {knowledge_dir}")
        return docs

    for path in knowledge_dir.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in LOADER_MAP:
            continue
        loader_cls = LOADER_MAP[path.suffix.lower()]
        try:
            loaded = loader_cls(str(path)).load()
            for d in loaded:
                # Registre de sources : chaque chunk garde une trace vérifiable du fichier d'origine
                d.metadata["source_file"] = path.name
                d.metadata["source_path"] = str(path)
            docs.extend(loaded)
            logger.info(f"Chargé : {path.name} ({len(loaded)} page(s)/section(s))")
        except Exception as e:
            logger.error(f"Échec du chargement de {path.name} : {e}")
    return docs


def split_documents(docs: List[Document]) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(docs)

    # Métadonnées d'observabilité (exigées par le protocole d'évaluation ORIENT'IA)
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = _doc_id(chunk.metadata.get("source_path", "unknown"), i)
        chunk.metadata["chunk_index"] = i
        chunk.metadata["n_chars"] = len(chunk.page_content)
        chunk.metadata.setdefault("titre", chunk.metadata.get("source_file", "Document"))

    logger.info(f"{len(chunks)} chunks générés (taille={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")
    return chunks


def build_vectorstore(chunks: List[Document]) -> Chroma:
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},                 # local, pas de clé API
        encode_kwargs={"normalize_embeddings": True},   # -> similarité cosinus propre
    )

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=PERSIST_DIR,
        collection_metadata={"hnsw:space": "cosine"},
    )
    logger.info(f"Base vectorielle persistée -> {PERSIST_DIR} ({COLLECTION_NAME})")
    return vectorstore


def run_ingestion() -> None:
    docs = load_documents()
    if not docs:
        logger.warning("Aucun document trouvé. Vérifiez data/knowledge/.")
        return
    chunks = split_documents(docs)
    build_vectorstore(chunks)
    logger.info("Ingestion terminée avec succès.")


if __name__ == "__main__":
    run_ingestion()