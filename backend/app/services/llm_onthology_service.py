import os
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from app.services.recommandation_prompt_service import recommandation_prompt_service


class ProfileExtractorSchema(BaseModel):
    competences: list[str] = Field(default=[], description="Liste des compétences/matières extraites et présentes dans l'ontologie")
    centres_interet: list[str] = Field(default=[], description="Liste des centres d'intérêt extraits et présents dans l'ontologie")


def extract_profile_from_prompt(user_prompt: str) -> ProfileExtractorSchema:
    valid_concepts = recommandation_prompt_service.get_all_concepts()

    # Injection de la totalité des concepts disponibles (sans le découpage [:60])
    ci_str = ", ".join(valid_concepts['centres_interet'])
    cp_str = ", ".join(valid_concepts['competences'])

    system_prompt = f"""
    Tu es un extracteur d'entités strict pour une ontologie d'orientation académique.
    Ton rôle est de faire correspondre les intentions de l'utilisateur avec UNIQUEMENT les identifiants valides fournis ci-dessous.

    --- VOCABULAIRE AUTORISÉ ---
    Centres d'intérêt valides : {ci_str}
    Compétences valides : {cp_str}
    ----------------------------

    RÈGLES DE VALIDATION :
    1. Ne génère JAMAIS un mot qui n'est pas explicitement présent dans les listes ci-dessus.
    2. Si l'utilisateur mentionne un synonyme, associe-le au concept valide le plus proche dans la liste.
    3. Si aucun terme ne correspond, laisse la liste vide [].
    """


    client = genai.Client(api_key="")

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type="application/json",
            response_schema=ProfileExtractorSchema,
            temperature=0.0,  # Garantit la réactivité stricte aux consignes
        ),
    )

    return ProfileExtractorSchema.model_validate_json(response.text)