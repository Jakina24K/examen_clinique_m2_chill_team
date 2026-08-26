import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
from app.schemas_tickets.ticket import AgentResponseSchema

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-2.5-flash"

def _clean_schema(schema: dict) -> dict:
    """Supprime récursivement additionalProperties pour rendre le schéma 100% compatible Gemini."""
    if isinstance(schema, dict):
        schema.pop("additionalProperties", None)
        schema.pop("additional_properties", None)
        for key, value in list(schema.items()):
            if isinstance(value, (dict, list)):
                _clean_schema(value)
    elif isinstance(schema, list):
        for item in schema:
            if isinstance(item, (dict, list)):
                _clean_schema(item)
    return schema


def call_llm_structured(system_prompt: str, user_content: str) -> AgentResponseSchema:
    """Appelle l'API Gemini et garantit une sortie conforme à AgentResponseSchema."""
    
    # Génération et nettoyage du schéma JSON Pydantic
    raw_schema = AgentResponseSchema.model_json_schema()
    cleaned_schema = _clean_schema(raw_schema)

    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=0.1,
        response_mime_type="application/json",
        response_schema=cleaned_schema,
    )

    response = client.models.generate_content(
        model=MODEL,
        contents=user_content,
        config=config,
    )

    # Validation et parsing dans le schéma Pydantic
    return AgentResponseSchema.model_validate_json(response.text)   