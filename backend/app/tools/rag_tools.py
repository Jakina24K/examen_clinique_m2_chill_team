"""
app/tools/rag_tools.py
------------------------
Outil RAG : recherche documentaire dense dans le corpus pédagogique ISPM.

Contrat de sortie : chaque élément retourné respecte `SourceItem`, validé à
l'exécution — pas seulement documenté. Toute dérive de retriever.py (ex:
renommage de champ) fait échouer cette validation immédiatement plutôt que
de propager un contrat cassé jusqu'au LLM.
"""

import logging
from typing import Any, Dict, List

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from app.rag.retriever import search_knowledge_base

logger = logging.getLogger(__name__)


class RechercherFormationInput(BaseModel):
    query: str = Field(..., description="Question ou sujet de formation à rechercher (ex: 'prérequis IGGLIA')")
    top_k: int = Field(4, ge=1, le=10, description="Nombre de passages à retourner")


class SourceItem(BaseModel):
    doc_id: str
    titre: str
    source_file: str
    score_pertinence: float = Field(..., ge=0.0, le=1.0)
    extrait: str


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
    raw_sources = search_knowledge_base(query, top_k=top_k)
    if not raw_sources:
        logger.info(f"rechercher_formation: aucun résultat pertinent pour '{query}'")
        return []

    validated = [SourceItem(**s.to_dict()) for s in raw_sources]
    return [item.model_dump() for item in validated]