"""
app/agent/agent.py
---------------------
Orchestrateur conversationnel ORIENT'IA - Version avec Connaissances ISPM Complètes

Caractéristiques avancées :
- Intégration du corpus complet des 16 filières
- Connaissances spécifiques sur TEE, TEH, ISAIA, IGGLIA, etc.
- Gestion de session avancée avec cache
- Validation post-LLM avec détection d'hallucinations
- Détection de conflits ML/Règles
- Système de fallback en cas d'erreur
- Traçabilité complète (observabilité)
"""

import re
import logging
import time
import threading
import json
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_google_genai import ChatGoogleGenerativeAI

from app.tools import AVAILABLE_TOOLS
from app.security.guardrails import (
    evaluate_security, 
    OFFICIAL_PROGRAMS, 
    get_program_name,
    is_valid_program,
    get_official_programs
)
from app.core.config import settings

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

MAX_HISTORY_LENGTH = 30
MAX_SESSIONS = 200
SESSION_TTL_SECONDS = 7200  # 2 heures
MAX_RETRIES = 3
CACHE_TTL_SECONDS = 600
MAX_RESPONSE_LENGTH = 3000

# ============================================================================
# CONNAISSANCES COMPLÈTES ISPM (16 FILIÈRES)
# ============================================================================

ISPM_KNOWLEDGE = {
    # --- TECHNIQUES DES AFFAIRES ---
    "CAA": {
        "nom_complet": "Commerce et Administration des Affaires",
        "domaine": "Techniques des Affaires",
        "objectif": "Former des étudiants au marketing, aux techniques commerciales, à l'organisation et au management des entreprises.",
        "matieres": "Marketing, Management, Comptabilité, Droit des affaires, Économie, Finance, RH, Négociation",
        "competences": "Gestion de projet, Négociation, Analyse de données, Stratégie marketing, Leadership",
        "pre_requis": "Baccalauréat (A, C, D), intérêt pour le commerce et la gestion",
        "debouchés": "Responsable commercial, Chef de produit, Chargé d'études marketing, Entrepreneur",
        "mots_cles": ["Marketing", "Management", "Commerce", "Vente", "Stratégie"]
    },
    "FIC": {
        "nom_complet": "Finances et Comptabilités",
        "domaine": "Techniques des Affaires",
        "objectif": "Former des étudiants dans les techniques quantitatives de gestion des entreprises.",
        "matieres": "Comptabilité générale, Comptabilité analytique, Finance, Contrôle de gestion, Audit, Fiscalité",
        "competences": "Gestion budgétaire, Analyse financière, Contrôle interne, Audit, Reporting",
        "pre_requis": "Baccalauréat (C, D, A2), bonnes aptitudes en mathématiques",
        "debouchés": "Comptable, Analyste financier, Contrôleur de gestion, Auditeur, Expert-comptable",
        "mots_cles": ["Comptabilité", "Finance", "Audit", "Contrôle", "Fiscalité"]
    },
    "DTJA": {
        "nom_complet": "Droit et Techniques Juridiques des Affaires",
        "domaine": "Techniques des Affaires",
        "objectif": "Former des juristes capables de maîtriser les techniques juridiques nationales et internationales.",
        "matieres": "Droit civil, Droit des affaires, Droit commercial, Droit du travail, Droit fiscal",
        "competences": "Rédaction d'actes juridiques, Conseil juridique, Analyse de contrats, Veille juridique",
        "pre_requis": "Baccalauréat (toutes séries), intérêt pour le droit et les affaires",
        "debouchés": "Juriste d'entreprise, Avocat, Conseiller juridique, Notaire, Magistrat",
        "mots_cles": ["Droit", "Juridique", "Contrats", "Société", "Fiscalité"]
    },
    "EMP": {
        "nom_complet": "Économie et Management de Projet",
        "domaine": "Techniques des Affaires",
        "objectif": "Former des économistes capables de réaliser des analyses économiques et de gérer des projets.",
        "matieres": "Microéconomie, Macroéconomie, Statistiques, Finance, Gestion de projet, Planification",
        "competences": "Analyse économique, Conduite de projets, Gestion budgétaire, Études de faisabilité",
        "pre_requis": "Baccalauréat (C, D, A2), intérêt pour l'économie et l'analyse",
        "debouchés": "Chef de projet, Économiste d'entreprise, Consultant, Analyste économique",
        "mots_cles": ["Économie", "Projet", "Management", "Stratégie", "Planification"]
    },
    
    # --- BIOTECHNOLOGIE ET AGRONOMIE ---
    "IAA": {
        "nom_complet": "Industrie Agroalimentaire",
        "domaine": "Biotechnologie et Agronomie",
        "objectif": "Former des cadres pour les industries agroalimentaires, maîtrisant transformation et contrôle qualité.",
        "matieres": "Microbiologie alimentaire, Biochimie, Transformation, Contrôle qualité, Sécurité sanitaire",
        "competences": "Maîtrise des chaînes de production, Contrôle qualité, Gestion de production, R&D",
        "pre_requis": "Baccalauréat (C, D, S), intérêt pour les sciences et l'alimentation",
        "debouchés": "Ingénieur agroalimentaire, Responsable qualité, Chef de production, Consultant",
        "mots_cles": ["Agroalimentaire", "Qualité", "Production", "Sécurité", "Alimentation"]
    },
    "PIP": {
        "nom_complet": "Pharmacologie et Industries Pharmaceutiques",
        "domaine": "Biotechnologie et Agronomie",
        "objectif": "Valoriser les plantes médicinales endémiques de Madagascar et former des professionnels pharmaceutiques.",
        "matieres": "Pharmacologie, Chimie pharmaceutique, Botanique, Toxicologie, Galénique",
        "competences": "R&D pharmaceutique, Extraction de principes actifs, Contrôle qualité, Conformité normes",
        "pre_requis": "Baccalauréat (C, D, S), très bonnes bases en chimie et biologie",
        "debouchés": "Pharmacien, Ingénieur pharmaceutique, R&D, Chef de production, Chercheur",
        "mots_cles": ["Pharmacologie", "Médicaments", "Santé", "R&D", "Qualité"]
    },
    "AEE": {
        "nom_complet": "Agriculture et Élevage",
        "domaine": "Biotechnologie et Agronomie",
        "objectif": "Former des jeunes capables d'appliquer les techniques modernes dans le monde rural.",
        "matieres": "Agronomie, Zootechnie, Biologie, Gestion des exploitations, Agroécologie",
        "competences": "Conduite d'exploitations, Agri-business, Gestion durable, Optimisation de production",
        "pre_requis": "Baccalauréat (C, D, S), intérêt pour l'agriculture et le monde rural",
        "debouchés": "Chef d'exploitation, Conseiller agricole, Agri-business manager, Ingénieur agronome",
        "mots_cles": ["Agriculture", "Élevage", "Agri-business", "Production", "Rural"]
    },
    
    # --- GÉNIE INDUSTRIEL ET GÉNIE CIVIL ---
    "EMII": {
        "nom_complet": "Électro-Mécanique et Informatique Industrielle",
        "domaine": "Génie Industriel et Génie Civil",
        "objectif": "Former des jeunes capables de maîtriser la mécanique et l'informatique industrielle.",
        "matieres": "Mécanique, Électrotechnique, Automatisme, Robotique, Programmation, CAO/DAO",
        "competences": "Conception et maintenance industrielle, Automatisation, Programmation industrielle",
        "pre_requis": "Baccalauréat (C, D, S), très bonnes bases en maths et physique",
        "debouchés": "Ingénieur électro-mécanicien, Responsable maintenance, Automaticien, Chef de projet",
        "mots_cles": ["Mécanique", "Électrotechnique", "Automatisme", "Robotique", "Industrie"]
    },
    "GCA": {
        "nom_complet": "Génie Civil et Architecture",
        "domaine": "Génie Industriel et Génie Civil",
        "objectif": "Former des jeunes capables d'améliorer les infrastructures et l'aménagement urbain.",
        "matieres": "Résistance des matériaux, Mécanique des sols, Structures, Topographie, Architecture",
        "competences": "Conception de structures, Études topographiques, Gestion de projets, Direction de chantiers",
        "pre_requis": "Baccalauréat (C, D, S), intérêt pour la construction et l'architecture",
        "debouchés": "Ingénieur civil, Architecte, Chef de chantier, Conducteur de travaux, Urbaniste",
        "mots_cles": ["Construction", "Architecture", "Infrastructures", "Béton", "Urbanisme"]
    },
    "ICMP": {
        "nom_complet": "Industries Chimiques, Minières et Pétrolières",
        "domaine": "Génie Industriel et Génie Civil",
        "objectif": "Former des jeunes capables de maîtriser les industries chimiques, minières et pétrolières.",
        "matieres": "Chimie générale, Génie chimique, Minéralurgie, Géologie, Forage, Pétrochimie",
        "competences": "Optimisation des procédés, Extraction de minerais, Sécurité industrielle, Environnement",
        "pre_requis": "Baccalauréat (C, D, S), très bonnes bases en chimie et physique",
        "debouchés": "Ingénieur chimiste, Ingénieur minier, Ingénieur pétrolier, Chef de projet minier",
        "mots_cles": ["Chimie", "Mines", "Pétrole", "Procédés", "Sécurité"]
    },
    
    # --- INFORMATIQUE ET TÉLÉCOMMUNICATION ---
    "IGGLIA": {
        "nom_complet": "Informatique de Gestion, Génie Logiciel et IA",
        "domaine": "Informatique et Télécommunication",
        "objectif": "Former des ingénieurs capables de maîtriser les techniques informatiques pour la gestion, le génie logiciel et l'IA.",
        "matieres": "Programmation (Java, Python), Génie logiciel, Bases de données, SI, IA, Réseaux",
        "competences": "Développement de logiciels de gestion, Modélisation SI, Gestion de projets, Bases de l'IA",
        "pre_requis": "Baccalauréat (C, D, S), intérêt pour l'informatique de gestion",
        "debouchés": "Ingénieur d'études, Développeur, Chef de projet, Consultant SI, Architecte logiciel",
        "mots_cles": ["Génie logiciel", "Gestion", "SI", "IA", "Développement"]
    },
    "ESIIA": {
        "nom_complet": "Électronique, Système Informatique et IA",
        "domaine": "Informatique et Télécommunication",
        "objectif": "Former des ingénieurs capables de maîtriser l'électronique et les systèmes informatiques.",
        "matieres": "Électronique, Architecture des ordinateurs, Systèmes embarqués, Réseaux, Télécoms, IA",
        "competences": "Conception électronique, Programmation embarquée, Admin systèmes, IoT",
        "pre_requis": "Baccalauréat (C, D, S), intérêt pour l'électronique et le matériel",
        "debouchés": "Ingénieur en électronique, Architecte système, Expert IoT, Ingénieur en télécommunications",
        "mots_cles": ["Électronique", "Systèmes", "Télécoms", "Embarqué", "IoT"]
    },
    "IMTICIA": {
        "nom_complet": "Informatique Multimédia, TIC et IA",
        "domaine": "Informatique et Télécommunication",
        "objectif": "Former des étudiants dans l'informatique multimédia et les nouvelles technologies.",
        "matieres": "Développement web/mobile, Multimédia, Design UX/UI, Réseaux, Cybersécurité, IA",
        "competences": "Conception d'applications, Création multimédia, Gestion de projets numériques",
        "pre_requis": "Baccalauréat (toutes séries), intérêt pour le multimédia et le web",
        "debouchés": "Développeur web/mobile, Chef de projet digital, Expert cybersécurité, Designer UI/UX",
        "mots_cles": ["Multimédia", "Web", "Mobile", "Digital", "Sécurité"]
    },
    "ISAIA": {
        "nom_complet": "Informatique, Statistique Appliquée et IA",
        "domaine": "Informatique et Télécommunication",
        "objectif": "Focaliser sur l'application des méthodes statistiques et informatiques dans l'Économie.",
        "matieres": "Mathématiques, Statistiques avancées, Data Science, Programmation (Python, R), IA, Big Data",
        "competences": "Analyse de données massives, Modélisation statistique, Data Mining, IA appliquée",
        "pre_requis": "Baccalauréat (C, D, S), très fortes aptitudes en mathématiques",
        "debouchés": "Data Scientist, Data Analyst, Statisticien, Ingénieur en IA, Actuaire",
        "mots_cles": ["Statistique", "Data Science", "IA", "Machine Learning", "Analyse"]
    },
    
    # --- TOURISME ---
    "TEE": {
        "nom_complet": "Tourisme et Environnement",
        "domaine": "Tourisme",
        "objectif": "Enseigner la richesse de l'environnement unique de Madagascar et de sa civilisation.",
        "description": "Madagascar est un des rares pays au monde à avoir un environnement unique et endémique. La filière TEE forme les futurs professionnels du tourisme.",
        "matieres": "Environnement, Écologie, Patrimoine, Culture, Tourisme durable",
        "competences": "Gestion des sites naturels, Écotourisme, Valorisation du patrimoine, Animation touristique",
        "pre_requis": "Baccalauréat (toutes séries), intérêt pour l'environnement et le tourisme",
        "debouchés": "Guide touristique spécialisé, Responsable développement durable, Gestionnaire de sites",
        "mots_cles": ["Tourisme", "Environnement", "Écologie", "Patrimoine", "Culture"]
    },
    "TEH": {
        "nom_complet": "Tourisme et Hôtellerie",
        "domaine": "Tourisme",
        "objectif": "Enseigner la richesse de la civilisation malagasy et maîtriser les techniques de l'art culinaire.",
        "description": "L'ISPM forme des étudiants capables de maîtriser les techniques de l'art culinaire national et international.",
        "matieres": "Hôtellerie, Restauration, Art culinaire, Gestion hôtelière, Service",
        "competences": "Management hôtelier, Cuisine, Gestion de restauration, Service client",
        "pre_requis": "Baccalauréat (toutes séries), intérêt pour l'hôtellerie et la restauration",
        "debouchés": "Manager hôtelier, Chef de cuisine, Responsable restauration, Gestionnaire touristique",
        "mots_cles": ["Tourisme", "Hôtellerie", "Restauration", "Art culinaire", "Gestion"]
    }
}

# Informations de comparaison
COMPARISONS = {
    "ISAIA_vs_IGGLIA": """
        **ISAIA** (Informatique, Statistique Appliquée et IA):
        - Focalisé sur les mathématiques, la statistique et la data science
        - Formation en analyse de données massives, machine learning, économétrie
        - Débouchés: Data Scientist, Data Analyst, Statisticien, Actuaire
        
        **IGGLIA** (Informatique de Gestion, Génie Logiciel et IA):
        - Focalisé sur le génie logiciel et les systèmes d'information
        - Formation en développement, bases de données, gestion de projets
        - Débouchés: Ingénieur d'études, Développeur, Chef de projet, Consultant SI
        
        **Différence clé**: ISAIA = données + statistiques + IA, IGGLIA = logiciel + gestion + IA
    """,
    "TEE_vs_TEH": """
        **TEE** (Tourisme et Environnement):
        - Focalisé sur la valorisation du patrimoine naturel et culturel
        - Formation en écologie, gestion des sites, écotourisme
        - Débouchés: Guide spécialisé, Responsable développement durable
        
        **TEH** (Tourisme et Hôtellerie):
        - Focalisé sur l'hébergement et la restauration
        - Formation en hôtellerie, art culinaire, gestion
        - Débouchés: Manager hôtelier, Chef de cuisine
        
        **Différence clé**: TEE = nature + culture, TEH = hôtellerie + restauration
    """
}

# ============================================================================
# PROMPT SYSTÈME ENRICHI
# ============================================================================

DISCLAIMER = (
    "ORIENT'IA est un outil d'aide à l'orientation. Ses recommandations ne "
    "remplacent ni l'avis d'un conseiller pédagogique ni une décision officielle d'admission."
)

# Génération du contexte ISPM à partir des connaissances
def _build_ispm_context() -> str:
    """Construit le contexte ISPM pour le prompt système."""
    context = "FORMATIONS OFFICIELLES DE L'ISPM:\n\n"
    
    for code, info in ISPM_KNOWLEDGE.items():
        context += f"**{code}** - {info['nom_complet']}\n"
        context += f"  Domaine: {info['domaine']}\n"
        context += f"  Objectif: {info['objectif']}\n"
        context += f"  Matières: {info['matieres']}\n"
        context += f"  Prérequis: {info['pre_requis']}\n"
        context += f"  Débouchés: {info['debouchés']}\n\n"
    
    return context

ISPM_CONTEXT = _build_ispm_context()

SYSTEM_PROMPT = f"""Tu es ORIENT'IA, un assistant d'orientation pédagogique pour l'ISPM.

**CONTEXTE ISPM (16 FILIÈRES OFFICIELLES):**

{ISPM_CONTEXT}

**RÈGLES DE SÉCURITÉ STRICTES (inviolables):**
1. Tu ne dois JAMAIS inventer une formation, un parcours, une règle d'admission qui n'apparaît pas dans les résultats de tes outils ou dans le contexte ci-dessus.
2. Tu ne dois JAMAIS déduire un trait de personnalité, une capacité ou un profil psychologique à partir du style d'écriture de l'utilisateur.
3. Tu ne dois JAMAIS baser une recommandation sur des critères discriminatoires (sexe, âge, origine, religion, orientation sexuelle, handicap).
4. Si un outil renvoie une erreur, reporte cela TEL QUEL.
5. En cas de conflit entre le modèle ML et les règles pédagogiques, SIGNALE explicitement le conflit.

**OPÉRATIONS À EFFECTUER:**
1. Pour les formations officielles: utiliser les informations du contexte ISPM
2. Pour les recommandations personnalisées: appeler `analyser_profil_ml`
3. Pour les prérequis: appeler `verifier_prerequis`
4. Pour les comparaisons: utiliser les données disponibles et appeler les outils appropriés

**COMMUNICATION:**
- Cite systématiquement les sources (titre/fichier)
- Indique le niveau d'incertitude
- Pose des questions si une information manque
- Termine par: {DISCLAIMER}

**RAPPEL**: Tu es un assistant pédagogique, pas un psychologue, pas un décideur administratif.
"""

# ============================================================================
# GESTIONNAIRE DE SESSIONS
# ============================================================================

class ConversationStore:
    """Gestionnaire de sessions avec TTL, cache et statistiques."""
    
    def __init__(self, max_sessions: int = MAX_SESSIONS, ttl_seconds: int = SESSION_TTL_SECONDS):
        self._store: Dict[str, Dict[str, Any]] = {}
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._max_sessions = max_sessions
        self._lock = threading.RLock()
        self._ttl_seconds = ttl_seconds
        self._stats = {
            "total_sessions": 0,
            "total_messages": 0,
            "cache_hits": 0,
            "cache_misses": 0,
        }
    
    def get(self, session_id: str) -> Optional[List[Any]]:
        """Récupère l'historique d'une session."""
        with self._lock:
            session_data = self._store.get(session_id)
            if not session_data:
                return None
            
            if datetime.now() - session_data["last_accessed"] > timedelta(seconds=self._ttl_seconds):
                del self._store[session_id]
                logger.info(f"Session {session_id} expirée")
                return None
            
            session_data["last_accessed"] = datetime.now()
            self._stats["total_sessions"] += 1
            return session_data["history"]
    
    def set(self, session_id: str, history: List[Any]) -> None:
        """Stocke l'historique d'une session."""
        with self._lock:
            self._evict_if_needed()
            self._store[session_id] = {
                "history": history,
                "last_accessed": datetime.now(),
                "created_at": self._store.get(session_id, {}).get("created_at", datetime.now()),
                "message_count": self._store.get(session_id, {}).get("message_count", 0) + 1,
            }
            self._stats["total_messages"] += 1
    
    def get_cache(self, key: str) -> Optional[Any]:
        """Récupère une valeur du cache."""
        with self._lock:
            cached = self._cache.get(key)
            if cached and datetime.now() - cached["timestamp"] < timedelta(seconds=CACHE_TTL_SECONDS):
                self._stats["cache_hits"] += 1
                return cached["value"]
        self._stats["cache_misses"] += 1
        return None
    
    def set_cache(self, key: str, value: Any) -> None:
        """Stocke une valeur dans le cache."""
        with self._lock:
            self._cache[key] = {"value": value, "timestamp": datetime.now()}
    
    def _evict_if_needed(self) -> None:
        with self._lock:
            if len(self._store) >= self._max_sessions:
                oldest = min(self._store.items(), key=lambda x: x[1]["last_accessed"])
                del self._store[oldest[0]]  # Doit être INDENTÉ dans le if
                logger.info(f"Session {oldest[0]} évincée")
    
    def clear_expired(self) -> None:
        """Supprime les sessions expirées."""
        now = datetime.now()
        expired = [
            sid for sid, data in self._store.items()
            if now - data["last_accessed"] > timedelta(seconds=self._ttl_seconds)
        ]
        for sid in expired:
            del self._store[sid]
        if expired:
            logger.info(f"{len(expired)} sessions expirées")
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques."""
        return {
            **self._stats,
            "active_sessions": len(self._store),
            "cache_size": len(self._cache),
        }


# ============================================================================
# INITIALISATION DE L'AGENT
# ============================================================================

def _get_llm() -> ChatGoogleGenerativeAI:
    """Initialisation du LLM."""
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.1,
        google_api_key=settings.GEMINI_API_KEY,
        timeout=30,
        max_retries=MAX_RETRIES,
    )


def _build_agent_executor() -> AgentExecutor:
    """Construction de l'agent."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])
    
    llm = _get_llm()
    agent = create_tool_calling_agent(llm, AVAILABLE_TOOLS, prompt)
    
    return AgentExecutor(
        agent=agent,
        tools=AVAILABLE_TOOLS,
        verbose=False,
        return_intermediate_steps=True,
        max_iterations=8,
        early_stopping_method="generate",
        handle_parsing_errors=True,
        max_execution_time=30,
    )

_agent_executor = None

def _get_agent_executor() -> AgentExecutor:
    """Lazy loading de l'agent."""
    global _agent_executor
    if _agent_executor is None:
        _agent_executor = _build_agent_executor()
    return _agent_executor


# ============================================================================
# TRAITEMENT DES RÉPONSES
# ============================================================================

def _extract_tool_trace(intermediate_steps) -> List[Dict[str, Any]]:
    """Extrait les traces des outils."""
    trace = []
    for action, observation in intermediate_steps:
        safe_observation = observation
        if isinstance(observation, str) and len(observation) > 1000:
            safe_observation = observation[:1000] + "... [truncated]"
        trace.append({
            "outil": action.tool,
            "parametres": action.tool_input,
            "resultat": safe_observation,
            "timestamp": datetime.now().isoformat(),
        })
    return trace


def _extract_sources(tool_trace: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    sources = []
    for step in tool_trace:
        if step["outil"] == "rechercher_formation":
            result = step["resultat"]
            if isinstance(result, list):
                for item in result:
                    if isinstance(item, dict):
                        sources.append({
                            "titre": item.get("titre", "Source"),
                            "fichier": item.get("source_file", ""), 
                            "contenu": item.get("extrait", "")[:300], 
                            "score_pertinence": item.get("score_pertinence"), 
                        })
    return sources


def _detect_hallucination(response: str, sources: List[Dict]) -> bool:
    """Détecte les hallucinations potentielles."""
    if len(response) > 500 and not sources:
        return True
    
    suspicious = [
        r"(?i)l'ispm propose.*?[0-9]+.*?formations",
        r"(?i)plus de.*?[0-9]+.*?étudiants",
        r"(?i)taux de réussite.*?[0-9]+%",
    ]
    for pattern in suspicious:
        if re.search(pattern, response.lower()):
            if not sources:
                return True
    return False


def _validate_response(response: str, sources: List[Dict], tool_trace: List[Dict]) -> Tuple[bool, str]:
    """Valide la réponse du LLM."""
    if DISCLAIMER[:30] not in response:
        return False, "Disclaimer absent"
    
    if _detect_hallucination(response, sources):
        return False, "Hallucination détectée"
    
    profiling = [
        r"(?i)personnalité (?:de type|de style)",
        r"(?i)traits (?:de|de votre) (?:caractère|personnalité)",
    ]
    for pattern in profiling:
        if re.search(pattern, response.lower()):
            return False, "Profilage psychologique détecté"
    
    return True, ""


def _format_response(response: str, sources: List[Dict], incertitude: str, conflict: Optional[str] = None) -> str:
    """Formate la réponse finale."""
    if DISCLAIMER not in response:
        response = f"{response}\n\n{DISCLAIMER}"
    
    incertitude_msg = f"\n\n⚠️ **Niveau d'incertitude**: {incertitude}"
    response += incertitude_msg
    
    if sources:
        source_text = "\n\n📚 **Sources:**\n"
        for i, s in enumerate(sources[:3], 1):
            titre = s.get("titre", "Source")
            source_text += f"  {i}. {titre}\n"
        response += source_text
    
    if conflict:
        response += f"\n\n⚠️ **Conflit**: {conflict}. Consultez un conseiller."
    
    if len(response) > MAX_RESPONSE_LENGTH:
        response = response[:MAX_RESPONSE_LENGTH] + "..."
    
    return response


# ============================================================================
# FONCTION PRINCIPALE
# ============================================================================

_conversation_store = ConversationStore()

def process_message(session_id: str, message: str) -> Dict[str, Any]:
    """Point d'entrée principal."""
    start_time = time.time()
    
    # 1. Garde-fous
    blocked, reason, warnings = evaluate_security(message)
    if blocked:
        logger.warning(f"[{session_id}] Message bloqué — raison={reason} signaux={warnings}")
        return {
            "reponse": f"Je ne peux pas traiter cette demande.\n\n**Raison**: {reason}",
            "sources": [], "outils_executes": [], "incertitude": "N/A",
            "avertissements": warnings,
            "temps_execution_s": round(time.time() - start_time, 2),
            "bloquee": True,
        }

    # 2. Session
    history = _conversation_store.get(session_id) or []
    if not history:
        logger.info(f"[{session_id}] Nouvelle session")

    # 3. Cache
    cache_key = hashlib.md5(f"{session_id}_{message}".encode()).hexdigest()
    cached = _conversation_store.get_cache(cache_key)
    if cached:
        logger.info(f"[{session_id}] Cache hit ({cache_key[:8]}...)")
        return {**cached, "temps_execution_s": round(time.time() - start_time, 2), "cache_hit": True}
    logger.debug(f"[{session_id}] Cache miss ({cache_key[:8]}...)")

    # 4. Agent
    executor = _get_agent_executor()
    try:
        result = executor.invoke({"input": message, "chat_history": history})
    except Exception:
        logger.error(f"[{session_id}] Échec de l'exécution de l'agent", exc_info=True)
        return {
            "reponse": f"Erreur technique. Veuillez réessayer.\n\n{DISCLAIMER}",
            "sources": [], "outils_executes": [], "incertitude": "Élevée",
            "avertissements": ["Une erreur technique est survenue côté serveur."],
            "temps_execution_s": round(time.time() - start_time, 2),
        }

    # 5. Extraction
    final_text = result.get("output", "")
    tool_trace = _extract_tool_trace(result.get("intermediate_steps", []))
    sources = _extract_sources(tool_trace)
    _log_tool_trace(session_id, tool_trace)

    # 6. Validation
    is_valid, err = _validate_response(final_text, sources, tool_trace)
    if not is_valid:
        logger.warning(f"[{session_id}] Réponse invalidée — raison={err}")
        final_text = f"Ma réponse nécessite une vérification. {DISCLAIMER}"
    
    # 7. Incertitude
    if not sources:
        incertitude = "Élevée - peu d'appui documentaire"
    elif len(tool_trace) < 2:
        incertitude = "Moyenne - support partiel"
    else:
        incertitude = "Faible - support documentaire"
    
    # 8. Formatage
    final_response = _format_response(final_text, sources, incertitude)
    
    # 9. Mémoire
    history.append(HumanMessage(content=message))
    history.append(AIMessage(content=final_response))
    if len(history) > MAX_HISTORY_LENGTH:
        history = history[-MAX_HISTORY_LENGTH:]
    _conversation_store.set(session_id, history)
    
    # 10. Cache
    _conversation_store.set_cache(cache_key, {
        "reponse": final_response,
        "sources": sources[:3],
        "outils_executes": tool_trace[:3],
        "incertitude": incertitude,
        "avertissements": warnings,
    })
    
    return {
        "reponse": final_response,
        "sources": sources,
        "outils_executes": tool_trace,
        "incertitude": incertitude,
        "avertissements": warnings,
        "temps_execution_s": round(time.time() - start_time, 2),
        "session_id": session_id,
        "cache_hit": False,
    }

def cleanup_expired_sessions() -> None:
    """Public wrapper so main.py can call this without reaching into the
    private _conversation_store."""
    _conversation_store.clear_expired()


def _log_tool_trace(session_id: str, tool_trace: List[Dict[str, Any]]) -> None:
    """PII-safe summary: tool name + rough status only. Full params/results
    already go to the DB trace and the structured JSON log — never duplicate
    that raw payload into the plaintext app log."""
    try:
        summary = []
        for t in tool_trace:
            res = t.get("resultat")
            statut = res.get("statut") if isinstance(res, dict) else "n/a"
            summary.append({"outil": t.get("outil"), "statut": statut})
        logger.info(f"[{session_id}] Outils exécutés: {summary}")
    except Exception:
        logger.debug(f"[{session_id}] Échec du log de trace outils", exc_info=True)


# ============================================================================
# UTILITAIRES
# ============================================================================

def get_program_info(code: str) -> Optional[Dict[str, Any]]:
    """Retourne les informations d'une filière."""
    return ISPM_KNOWLEDGE.get(code.upper())


def compare_programs(code1: str, code2: str) -> Optional[str]:
    """Compare deux filières."""
    key = f"{code1.upper()}_vs_{code2.upper()}"
    return COMPARISONS.get(key)


def get_stats() -> Dict[str, Any]:
    """Retourne les statistiques du système."""
    return _conversation_store.get_stats()


# ============================================================================
# TESTS
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("TESTS ORIENT'IA AGENT")
    print("=" * 60)
    
    print(f"\nFilières chargées: {len(ISPM_KNOWLEDGE)}")
    print(f"Codes: {', '.join(ISPM_KNOWLEDGE.keys())}")
    
    print("\nExemple de comparaison ISAIA vs IGGLIA:")
    print(compare_programs("ISAIA", "IGGLIA")[:200] + "...")