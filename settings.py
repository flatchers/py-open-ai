import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_url: str = "sqlite+aiosqlite:///./openai.db"
    POSTGRES_HOST: str | None = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", 5432))
    POSTGRES_USER: str | None = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str | None = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB: str | None = os.getenv("POSTGRES_DB")

    OPENAI_SECRET_KEY: str | None = os.getenv("OPENAI_SECRET_KEY")

    class Config:
        env_file = ".env"


settings = Settings()
