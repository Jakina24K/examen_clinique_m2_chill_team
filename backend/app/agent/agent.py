"""
app/agent/agent.py
---------------------
Orchestrateur conversationnel ORIENT'IA.

Pipeline :
  1. Garde-fous (sécurité, refus de profilage psychologique / invention de formation)
     -> déterministe, exécuté AVANT tout appel LLM, coût nul.
  2. Agent LangChain (tool-calling) : le LLM décide quels outils appeler
       -> RAG          : rechercher_formation   (probabiliste, dense retrieval)
       -> ML            : analyser_profil_ml     (probabiliste, classifieur)
       -> Symbolique    : verifier_prerequis     (déterministe, règles/ontologie)
  3. Formatage final : réponse argumentée, citations vérifiables, incertitude
     explicite, trace complète des outils appelés (observabilité).

Mémoire de conversation : par session_id, en mémoire ici (remplacer par
Redis/Postgres en production — voir app/core/database.py existant).
"""

import logging
import time
from typing import Dict, List, Any

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_google_genai import ChatGoogleGenerativeAI

from app.tools.tools import AVAILABLE_TOOLS
from app.security.guardrails import evaluate_security
from app.core.config import settings

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------
# Mémoire de conversation (in-memory, clé = session_id)
# --------------------------------------------------------------------------
_CONVERSATION_STORE: Dict[str, List[Any]] = {}

DISCLAIMER = (
    "ORIENT'IA est un outil d'aide à l'orientation. Ses recommandations ne "
    "remplacent ni l'avis d'un conseiller pédagogique ni une décision officielle d'admission."
)

SYSTEM_PROMPT = f"""Tu es ORIENT'IA, un assistant d'orientation pédagogique pour l'ISPM.

RÈGLES STRICTES :
1. Tu ne dois JAMAIS inventer une formation, un parcours ou une règle d'admission
   qui n'apparaît pas dans les résultats de tes outils. Si l'information est
   absente, dis-le explicitement et propose d'orienter vers l'administration.
2. Tu ne dois JAMAIS déduire un trait de personnalité, une capacité ou un profil
   psychologique à partir du style d'écriture de l'utilisateur. Utilise
   uniquement les préférences que l'utilisateur déclare explicitement
   (matières, compétences, centres d'intérêt).
3. Pour toute recommandation de parcours, appelle `analyser_profil_ml` avec le
   profil déclaré. Pour toute question factuelle sur une formation, appelle
   `rechercher_formation`. Pour vérifier une éligibilité, appelle
   `verifier_prerequis`.
4. Cite systématiquement tes sources (titre / fichier) quand tu t'appuies sur
   des résultats RAG.
5. Si le modèle ML et les règles symboliques se contredisent (ex : le ML
   recommande un parcours mais les prérequis ne sont pas satisfaits), signale
   EXPLICITEMENT ce conflit à l'utilisateur au lieu de le masquer.
6. Indique toujours ton niveau d'incertitude. Pose une question de
   clarification si une information essentielle manque, plutôt que de deviner.
7. Termine toute recommandation par : "{DISCLAIMER}".
8. Si un outil renvoie un statut d'erreur ou 'formation_inconnue' ou 'profil_insuffisant',
   reporte cela TEL QUEL à l'utilisateur (ne reformule pas en supposant une réponse positive).
"""


def _get_llm() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.1,
        google_api_key=settings.GEMINI_API_KEY,   # <-- explicit, not env-var magic
    )

def _build_agent_executor() -> AgentExecutor:
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
        return_intermediate_steps=True,  # indispensable pour tracer les outils appelés
        max_iterations=6,
    )


_agent_executor = None


def _get_agent_executor() -> AgentExecutor:
    global _agent_executor
    if _agent_executor is None:
        _agent_executor = _build_agent_executor()
    return _agent_executor


def _extract_tool_trace(intermediate_steps) -> List[Dict[str, Any]]:
    """Transforme les intermediate_steps LangChain en trace exploitable (observabilité)."""
    trace = []
    for action, observation in intermediate_steps:
        trace.append({
            "outil": action.tool,
            "parametres": action.tool_input,
            "resultat": observation,
        })
    return trace


def process_message(session_id: str, message: str) -> Dict[str, Any]:
    """
    Point d'entrée principal appelé par la route FastAPI (ex: POST /chat).

    Retourne un contrat structuré : réponse, sources RAG, outils appelés
    (traçant séparément ML et symbolique), incertitude, et temps d'exécution
    — conforme aux "traces attendues" du protocole d'évaluation ORIENT'IA.
    """
    start = time.time()

    # --- 1. Garde-fous AVANT tout appel LLM (rapide, déterministe, coût nul) ---
    blocked, reason, warnings = evaluate_security(message)
    if blocked:
        logger.warning(f"[session={session_id}] Requête bloquée : {reason}")
        return {
            "reponse": (
                f"Je ne peux pas répondre à cette demande. {reason} "
                "Si votre besoin est légitime, reformulez-le en vous limitant aux "
                "informations que vous souhaitez déclarer explicitement (matières, "
                "compétences, centres d'intérêt)."
            ),
            "sources": [],
            "outils_executes": [],
            "incertitude": "N/A - requête bloquée par garde-fou",
            "avertissements": warnings + [reason],
            "temps_execution_s": round(time.time() - start, 2),
        }

    # --- 2. Historique de conversation ---
    history = _CONVERSATION_STORE.setdefault(session_id, [])

    # --- 3. Exécution de l'agent (RAG + ML + Symbolique orchestrés par le LLM) ---
    executor = _get_agent_executor()
    try:
        result = executor.invoke({"input": message, "chat_history": history})
    except Exception as e:
        logger.error(f"[session={session_id}] Erreur agent : {e}")
        return {
            "reponse": "Une erreur technique est survenue. Merci de réessayer.",
            "sources": [],
            "outils_executes": [],
            "incertitude": "élevée - échec technique",
            "avertissements": [str(e)],
            "temps_execution_s": round(time.time() - start, 2),
        }

    final_text = result["output"]
    tool_trace = _extract_tool_trace(result.get("intermediate_steps", []))

    # Extraction des sources RAG depuis la trace, pour affichage/citations séparés
    sources = []
    for step in tool_trace:
        if step["outil"] == "rechercher_formation" and isinstance(step["resultat"], list):
            sources.extend(step["resultat"])

    # --- 4. Mise à jour de la mémoire (bornée pour limiter coût/latence) ---
    history.append(HumanMessage(content=message))
    history.append(AIMessage(content=final_text))
    _CONVERSATION_STORE[session_id] = history[-20:]

    return {
        "reponse": final_text,
        "sources": sources,
        "outils_executes": tool_trace,
        "incertitude": "faible" if sources or tool_trace else "élevée - peu d'appui documentaire ou d'outils",
        "avertissements": warnings,
        "temps_execution_s": round(time.time() - start, 2),
    }