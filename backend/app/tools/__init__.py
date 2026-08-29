from app.tools.rag_tools import rechercher_formation
from app.tools.ml_tools import analyser_profil_ml
from app.tools.symbolic_tools import verifier_prerequis

AVAILABLE_TOOLS = [rechercher_formation, analyser_profil_ml, verifier_prerequis]