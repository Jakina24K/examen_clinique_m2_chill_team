import sys
from pathlib import Path

# Ajoute le dossier racine du projet au path Python
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.schemas_tickets.ticket import TicketInput
from app.agent.agent import process_ticket

# 1. Instanciation du ticket de test
ticket_test = TicketInput(
    ticket_id="TCK-TEST-01",
    description="Depuis ce matin je ne peux plus accéder au VPN. J'ai essayé de redémarrer mon ordinateur.",
    utilisateur="Rakoto"
)

# 2. Exécution du pipeline complet
result = process_ticket(ticket_test)

# 3. Affichage du résultat JSON
print(result.model_dump_json(indent=2))