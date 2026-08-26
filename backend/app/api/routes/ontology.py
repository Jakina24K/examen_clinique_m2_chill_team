from fastapi import APIRouter, HTTPException
from app.services.recommandation_service import recommandation_service
from pydantic import BaseModel, Field
from app.services.llm_onthology_service import extract_profile_from_prompt
from app.services.recommandation_prompt_service import recommandation_prompt_service

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

class PromptInput(BaseModel):
    prompt: str

@routeur.post("/prompt")
def get_recommandation_from_prompt(input_data: PromptInput):
    # 1. Extraction via Gemini
    try:
        profile_extracted = extract_profile_from_prompt(input_data.prompt)
    except Exception as e:
        # Renvoie l'erreur exacte dans le JSON Swagger au lieu de crasher en 500
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'extraction Gemini : {type(e).__name__} - {str(e)}"
        )

    # 2. Requête SPARQL
    try:
        results = recommandation_prompt_service.get_recommandation_dynamique(
            competences=profile_extracted.competences,
            centres_interet=profile_extracted.centres_interet,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la requête SPARQL : {type(e).__name__} - {str(e)}"
        )

    # 3. Réponse
    return {
        "prompt_utilisateur": input_data.prompt,
        "profil_extrait": profile_extracted.model_dump(),
        "recommandations": results,
    }