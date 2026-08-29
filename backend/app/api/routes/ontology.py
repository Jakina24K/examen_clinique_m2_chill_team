from fastapi import APIRouter, HTTPException
from app.services.recommandation_service import recommandation_service
from pydantic import BaseModel, Field

routeur = APIRouter()

class ProfileExtractorSchema(BaseModel):
    competences: list[str] = Field(
        description="Liste des identifiants de compétences détectées dans le texte (ex: ['CP_Informatique', 'CP_Maths', 'CP_Gestion'])"
    )
    centres_interet: list[str] = Field(
        default=[],
        description="Centres d'intérêt mentionnés par l'étudiant (ex: ['JeuxVideo', 'IA', 'Design'])"
    )
    matieres_pref: list[str] = Field(
        default=[],
        description="Matières préférées de l'étudiant (ex: ['Algèbre', 'Physique', 'Anglais'])"
    )

class DynamicProfileInput(BaseModel):
    competences: list[str]  # Exemple: ["CP_Informatique", "CP_Maths"]
    centres_interet: list[str] | None = None
    matieres_pref: list[str] | None = None

@routeur.post("/dynamique")
def get_recommandation_dynamique(profile: DynamicProfileInput):
    results = recommandation_service.get_recommandation_dynamique(
        competences=profile.competences,
        centres_interet=profile.centres_interet,
        matieres_pref=profile.matieres_pref
    )
    if not results:
        raise HTTPException(status_code=404, detail="Aucun parcours correspondant trouvé")
    return results
