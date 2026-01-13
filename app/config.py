from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path
import os

# Obtener la ruta del directorio raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Email
    SMTP_HOST: str
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASSWORD: str
    SMTP_FROM_NAME: str = "Cineminha"
    SMTP_FROM_EMAIL: str = "noreply@cineminha.com"
    SMTP_USE_TLS: bool = True
    SMTP_USE_SSL: bool = False

    # Variables de email - Brevo
    BREVO_API_KEY: str = ""
    EMAIL_FROM: str = "victorjoseruizsoto4@gmail.com"  # Puede ser cualquier email
    EMAIL_FROM_NAME: str = "Cineminha"

    # Frontend
    FRONTEND_URL: str = "http://localhost:4200"

    # TMDB API
    TMDB_API_KEY: Optional[str] = None
    TMDB_BASE_URL: str = "https://api.themoviedb.org/3"

    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost:4200",
        "http://localhost:4201",
    ]

    class Config:
        env_file = str(ENV_FILE)  # Ruta absoluta al .env
        env_file_encoding = 'utf-8'
        case_sensitive = True
        extra = 'ignore'


# Crear instancia de settings
settings = Settings()
