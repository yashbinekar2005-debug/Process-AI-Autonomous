import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # LLM Configuration (Ollama preferred, Gemini fallback)
    LLM_PROVIDER: str = "ollama"  # "ollama" or "gemini"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # Web Search
    TAVILY_API_KEY: str = ""

    # Persistence
    REDIS_URL: str = "redis://localhost:6379"
    CHROMA_DB_PATH: str = "./chroma_db"

    # Server
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Action Agent
    SLACK_WEBHOOK_URL: str = ""
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_TO: str = "admin@enterprise.com"

    # Retry
    LLM_MAX_RETRIES: int = 3
    LLM_RETRY_DELAY: float = 2.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
