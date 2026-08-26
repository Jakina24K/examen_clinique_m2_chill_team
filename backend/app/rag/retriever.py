# import os
# from typing import List
# import chromadb
# from dotenv import load_dotenv
# from app.schemas.ticket import SourceRAG

# load_dotenv()

# PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# def search_knowledge_base(query: str, top_k: int = 2) -> List[SourceRAG]:
#     """Recherche RAG résiliente dans ChromaDB."""
#     try:
#         if not os.path.exists(PERSIST_DIR):
#             return []

#         client = chromadb.PersistentClient(path=PERSIST_DIR)
        
#         try:
#             collection = client.get_collection(name="knowledge_base")
#         except Exception:
#             return []

#         results = collection.query(
#             query_texts=[query],
#             n_results=top_k
#         )

#         sources = []
#         if results and results.get('documents') and len(results['documents']) > 0:
#             for i in range(len(results['documents'][0])):
#                 doc_text = results['documents'][0][i]
#                 metadata = results['metadatas'][0][i] if results.get('metadatas') else {}
#                 distances = results.get('distances')
#                 distance = distances[0][i] if distances and len(distances) > 0 else 0.2
                
#                 score = max(0.0, min(1.0, round(1.0 - (distance / 2), 2)))

#                 sources.append(SourceRAG(
#                     doc_id=metadata.get("doc_id", "KB-UNK"),
#                     titre=metadata.get("titre", "Document"),
#                     score_pertinence=score,
#                     extrait=doc_text
#                 ))
#         return sources
#     except Exception as e:
#         print(f"Avertissement RAG (mode dégradé) : {e}")
#         # En cas d'erreur réseau/Chroma, renvoie un mock RAG pour ne pas bloquer l'agent
#         return [
#             SourceRAG(
#                 doc_id="KB-NET-01",
#                 titre="Guide Dépannage VPN",
#                 score_pertinence=0.85,
#                 extrait="Procédure VPN: En cas de problème de connexion VPN, vérifier l'état du réseau local et redémarrer le client VPN."
#             )
#         ]

from typing import List
from app.schemas_tickets.ticket import SourceRAG

def search_knowledge_base(query: str, top_k: int = 2) -> List[SourceRAG]:
    """Mock RAG instantané pour valider le pipeline sans dépendre de téléchargements ONNX."""
    return [
        SourceRAG(
            doc_id="KB-NET-01",
            titre="Guide Dépannage VPN",
            score_pertinence=0.88,
            extrait="En cas de problème VPN: Vérifier la connexion locale, puis redémarrer le client VPN."
        )
    ]