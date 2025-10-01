from typing import Any, List, Optional

from pydantic import AnyHttpUrl, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Project
    PROJECT_NAME: str = "Mahaguru AI API"
    API_V1_STR: str = "/api/v1"
    ENV: str = "development"
    # Compatibility with logging_config which expects ENVIRONMENT and LOG_LEVEL
    ENVIRONMENT: str = "local"
    LOG_LEVEL: str = "INFO"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 60 minutes
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    RESET_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_COOKIE_NAME: str = "refresh_token"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # Frontend dev server
        "http://localhost:5000",  # Alternative frontend port
        "http://localhost:8000",  # Backend dev server
        "http://127.0.0.1:3000",  # Frontend dev server (alternative)
        "http://127.0.0.1:5000",  # Alternative frontend port
        "http://127.0.0.1:8000",  # Backend dev server (alternative)
    ]

    # Dev/Feature flags
    DEV_MODE: bool = False
    STUDENTGPT_DISABLED: bool = False

    # Server/runtime limits
    STUDENTGPT_TIMEOUT_SECONDS: int = 60
    MAX_REQUEST_BODY_BYTES: int = 1_000_000  # 1 MB default for chat endpoints

    # Database
    POSTGRES_SERVER: str = "db"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "mahaguru"
    DATABASE_URI: Optional[PostgresDsn] = None

    # Weaviate
    WEAVIATE_URL: str = "http://weaviate:8080"
    WEAVIATE_API_KEY: Optional[str] = None
    WEAVIATE_BATCH_SIZE: int = 100
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    
    # OpenAI
    #OPENAI_API_KEY: Optional[str] = None

    # Hugging Face & Gemini
    HUGGINGFACE_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None

    # Model configuration
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    @field_validator("DATABASE_URI", mode='before')
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], values) -> Any:
        if isinstance(v, str):
            return v
        
        return str(PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.data.get("POSTGRES_USER"),
            password=values.data.get("POSTGRES_PASSWORD"),
            host=values.data.get("POSTGRES_SERVER"),
            port=values.data.get("POSTGRES_PORT", 5432),
            path=f"/{values.data.get('POSTGRES_DB') or ''}"
        ))
    
    model_config = SettingsConfigDict(
    case_sensitive=True,
    env_file="../.env",  # Look in parent directory
    env_file_encoding="utf-8",
    extra="ignore"
)

settings = Settings()