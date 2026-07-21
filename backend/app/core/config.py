from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"

    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    frontend_origin: str = "http://localhost:5173"
    env: str = "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()
