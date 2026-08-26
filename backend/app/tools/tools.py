import json
from app.schemas_tickets.ticket import ToolCallLog

SIMULATED_USERS = {
    "jean.dupont": {"statut": "actif", "poste": "POSTE-042", "role": "Finance"},
    "admin.test": {"statut": "verrouille", "poste": "POSTE-001", "role": "IT"}
}

SIMULATED_SERVICES = {
    "VPN": "actif",
    "Email": "actif",
    "ERP": "incident_majeur",
    "Internet": "actif"
}


def verifier_utilisateur(user_id: str) -> ToolCallLog:
    """Consulte les informations d'un utilisateur."""
    params = json.dumps({"user_id": user_id})
    if user_id in SIMULATED_USERS:
        data = SIMULATED_USERS[user_id]
        return ToolCallLog(
            outil="rechercher_utilisateur",
            parametres_json=params,
            statut="succes",
            resultat=f"Utilisateur trouvé: {data}"
        )
    return ToolCallLog(
        outil="rechercher_utilisateur",
        parametres_json=params,
        statut="succes",
        resultat="Utilisateur non identifié dans l'annuaire."
    )


def verifier_etat_service(service_name: str) -> ToolCallLog:
    """Vérifie le statut opérationnel d'un service IT."""
    params = json.dumps({"service": service_name})
    service_key = service_name.upper()
    for key, status in SIMULATED_SERVICES.items():
        if key in service_key:
            return ToolCallLog(
                outil="verifier_etat_service",
                parametres_json=json.dumps({"service": key}),
                statut="succes",
                resultat=f"Statut du service {key}: {status}"
            )
    return ToolCallLog(
        outil="verifier_etat_service",
        parametres_json=params,
        statut="succes",
        resultat=f"Service {service_name} : Aucun incident global signalé."
    )