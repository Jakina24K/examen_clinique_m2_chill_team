import os
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from app.services.recommandation_prompt_service import recommandation_prompt_service


class ProfileExtractorSchema(BaseModel):
    competences: list[str] = Field(default=[], description="Liste des compétences ou matières (ex: Mathematiques, Programmation)")
    centres_interet: list[str] = Field(default=[], description="Liste des centres d'intérêt (ex: Informatique, IntelligenceArtificielle)")


def extract_profile_from_prompt(user_prompt: str) -> ProfileExtractorSchema:
    valid_concepts = recommandation_prompt_service.get_all_concepts()

    ci_list = valid_concepts['centres_interet']
    cp_list = valid_concepts['competences']

    system_prompt = f"""
    Tu es un assistant d'orientation académique.
    Analyse le texte utilisateur et extrais les DOMAINES, MATIÈRES, COMPÉTENCES et CENTRES D'INTÉRÊT mentionnés.

    Valeurs autorisées :
    - Centres d'intérêt / Domaines : {', '.join(ci_list[:60])}
    - Compétences / Matières : {', '.join(cp_list[:60])}

    Exemples d'extraction attendue :
    - "je suis passionné d'informatique, et de math" -> centres_interet: ["Informatique"], competences: ["Mathematiques"]
    - "j'aime le dev web et l'IA" -> centres_interet: ["IntelligenceArtificielle", "DeveloppementWeb"]

    CONSIGNE STRICTE :
    - Ne renvoie JAMAIS de mots de métadonnées comme "competences", "aPourCentreInteret", "centreInterets" ou "developpe".
    - Ne renvoie que les VRAIS NOMS de domaines ou compétences présents dans la liste.
    """

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("La clé GEMINI_API_KEY n'est pas définie dans l'environnement.")

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type="application/json",
            response_schema=ProfileExtractorSchema,
            temperature=0.0,
        ),
    )

    raw_text = response.text.encode("utf-8").decode("utf-8")
    return ProfileExtractorSchema.model_validate_json(raw_text)