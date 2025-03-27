from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    ANTHROPIC_API_KEY: str
    DATABASE_URL: Optional[str] = None
    TAVILY_API_KEY: str
    GROQ_API_KEY: str

    model_config = SettingsConfigDict(env_file='.env', extra='allow')


settings = Settings()
