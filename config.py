import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    GEMINI_API_KEY: str = ""
    TAVILY_API_KEY: str = ""
    REDIS_URL: str = "redis://localhost:6379"
    CHROMA_DB_PATH: str = "./chroma_db"
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    SLACK_WEBHOOK_URL: str = ""
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_TO: str = "admin@enterprise.com"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
