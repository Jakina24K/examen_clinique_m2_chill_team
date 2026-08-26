from app.schemas_tickets.ticket import TicketInput, AgentResponseSchema
from app.security.guardrails import evaluate_security
from app.tools.tools import verifier_utilisateur, verifier_etat_service
from app.rag.retriever import search_knowledge_base
from app.llm.client import call_llm_structured
from app.llm.prompts import SYSTEM_PROMPT


def process_ticket(ticket: TicketInput) -> AgentResponseSchema:
    """
    Orchestrateur principal :
    1. Garde-fous de Sécurité
    2. Exécution des outils de diagnostic
    3. RAG (Recherche Documentaire)
    4. Synthèse et Structuration par le LLM
    """
    # 1. Garde-fous de sécurité
    requires_validation, security_reason, warnings = evaluate_security(ticket.description)

    # 2. Exécution d'outils
    tool_logs = []
    tool_logs.append(verifier_utilisateur(ticket.utilisateur))
    tool_logs.append(verifier_etat_service(ticket.description))

    # 3. Recherche RAG
    rag_sources = search_knowledge_base(ticket.description, top_k=2)

    # Contextualisation pour le prompt LLM
    sources_text = "\n".join([f"- [{s.doc_id}] {s.titre}: {s.extrait}" for s in rag_sources])
    tools_text = "\n".join([f"- Outil '{t.outil}' ({t.statut}): {t.resultat}" for t in tool_logs])

    user_payload = f"""
    --- DÉTAILS DU TICKET ---
    ID: {ticket.ticket_id}
    Utilisateur: {ticket.utilisateur}
    Description: {ticket.description}

    --- CONTEXTE SÉCURITÉ & GARDE-FOUS ---
    Validation Humaine Recommandée: {requires_validation}
    Raison Sécurité: {security_reason if security_reason else 'Aucune alerte'}

    --- RÉSULTATS DES OUTILS EXÉCUTÉS ---
    {tools_text}

    --- SOURCES RAG DISPONIBLES ---
    {sources_text if sources_text else 'Aucune fiche pertinente trouvée'}
    """

    # 4. Appel LLM Structuré
    response = call_llm_structured(
        system_prompt=SYSTEM_PROMPT,
        user_content=user_payload
    )

    # Override de la sécurité pour garantir le respect strict des garde-fous
    if requires_validation:
        response.validation_humaine_requise = True
        response.raison_validation = security_reason

    # Injection des traces RAG et Outils dans le contrat final
    response.sources = rag_sources
    response.outils_executes = tool_logs

    return response