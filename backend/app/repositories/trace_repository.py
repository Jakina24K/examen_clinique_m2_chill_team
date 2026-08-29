# app/repositories/trace_repository.py  (NEW)
import json
from typing import Any, Dict
from sqlalchemy.orm import Session

from app.models.sessionConversation import SessionConversation
from app.models.message import Message
from app.models.reponse import Reponse
from app.models.trace import Trace


def get_or_create_session(db: Session, external_session_id: str) -> SessionConversation:
    session = (
        db.query(SessionConversation)
        .filter(SessionConversation.external_session_id == external_session_id)
        .first()
    )
    if session is None:
        session = SessionConversation(external_session_id=external_session_id)
        db.add(session)
        db.flush()  # obtient session.id sans committer
    return session


def save_interaction(db: Session, external_session_id: str, user_message: str, agent_result: Dict[str, Any]) -> None:
    """Un seul commit atomique : soit tout est sauvegardé, soit rien (pas d'état
    DB partiel en cas d'erreur en cours de route)."""
    try:
        session = get_or_create_session(db, external_session_id)

        message = Message(session_id=session.id, role="user", contenu=user_message)
        db.add(message)
        db.flush()

        trace = Trace(
            session_id=session.id,
            message_id=message.id,
            passages_recuperes=agent_result.get("sources", []),
            scores_recherche=[s.get("score_pertinence") for s in agent_result.get("sources", [])],
            outils_appeles=agent_result.get("outils_executes", []),
            ml_input_output=next(
                (s for s in agent_result.get("outils_executes", []) if s.get("outil") == "analyser_profil_ml"),
                None,
            ),
            reponse_finale=agent_result.get("reponse"),
            latence_ms=int(agent_result.get("temps_execution_s", 0) * 1000),
            erreurs=json.dumps(agent_result.get("avertissements", [])) if agent_result.get("avertissements") else None,
        )
        db.add(trace)
        db.flush()

        db.add(Reponse(session_id=session.id, message_id=message.id, trace_id=trace.id, contenu=agent_result.get("reponse", "")))
        db.commit()
    except Exception:
        db.rollback()
        raise