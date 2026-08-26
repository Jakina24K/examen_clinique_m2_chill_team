import os
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

load_dotenv()

PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")


def init_and_populate_db():
    """Initialise ChromaDB avec des procédures techniques fictives pour le RAG."""
    client = chromadb.PersistentClient(path=PERSIST_DIR)
    
    # Utilisation du modèle d'embedding par défaut de ChromaDB / Sentence Transformers
    collection = client.get_or_create_collection(name="knowledge_base")

    documents = [
        "Procédure VPN: En cas de problème de connexion VPN, vérifier l'état du réseau local, redémarrer le client VPN, puis contacter le Support N1 si le problème persiste.",
        "Politique de Sécurité: Toute modification de droits d'accès ou réinitialisation de mot de passe requiert obligatoirement une validation humaine du responsable IAM.",
        "Panne ERP: Un incident majeur est en cours sur l'ERP. L'équipe Infrastructure intervient. Temps de rétablissement estimé : 2 heures.",
        "Demande incomplète: Si un utilisateur signale un problème sans préciser le message d'erreur ou l'équipement concerné, demander systématiquement une capture d'écran et le nom du poste."
    ]

    metadatas = [
        {"doc_id": "KB-NET-01", "titre": "Guide Dépannage VPN"},
        {"doc_id": "KB-SEC-01", "titre": "Politique de Sécurité & Droits d'Accès"},
        {"doc_id": "KB-INFRA-02", "titre": "Status Incident ERP"},
        {"doc_id": "KB-PROC-01", "titre": "Guide de Qualification de Ticket"}
    ]

    ids = ["doc_1", "doc_2", "doc_3", "doc_4"]

    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    print("Base de connaissances ChromaDB initialisée avec succès !")


if __name__ == "__main__":
    init_and_populate_db()