import json
from typing import Dict, Any

from google import genai
from google.genai import types
from ml.data.raw.prompt import get_prompt
from app.core.config import settings
import os

api_key_ml = os.environ.get(settings.GEMINI_API_KEY_ML)


client = genai.Client(api_key=api_key_ml)


def extract_orientation_data(text: str) -> Dict[str, Any]:
    """
    Extrait les informations d'orientation d'un texte étudiant
    à l'aide de Gemini.
    """

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=get_prompt(text),
            config=types.GenerateContentConfig(
                response_mime_type="application/json", temperature=0
            ),
        )

        content = response.text

        if not content:
            raise ValueError("Gemini a retourné une réponse vide.")

        data = json.loads(content)
        print("Data dans extract : ", data)
        if not isinstance(data, dict):
            raise ValueError("La réponse de Gemini n'est pas un objet JSON.")

        return data

    except json.JSONDecodeError as e:
        raise ValueError(f"La réponse de Gemini n'est pas un JSON valide : {e}")

    except Exception as e:
        raise RuntimeError(f"Erreur lors de l'appel à Gemini : {e}")
