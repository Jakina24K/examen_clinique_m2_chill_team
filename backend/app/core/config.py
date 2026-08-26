from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Base de données PostgreSQL
    DATABASE_URL: str = "postgresql://postgres:votre_mot_de_passe@localhost:5432/DB_Hackathon"
    
    # Sécurité & Auth
    SECRET_KEY: str = "votre_cle_secrete_jwt_super_securisee"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    
    # Application & AI
    APP_NAME: str = "My FastAPI App"
    DEBUG: bool = True
    GEMINI_API_KEY: Optional[str] = None
    CHROMA_PERSIST_DIR: str = "./chroma_db"

    # Configuration Pydantic Settings
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Empêche les erreurs si des variables supplémentaires sont dans le .env
    )

settings = Settings()