from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    openai_base_url: str | None = None
    openai_embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536
    whatsapp_token: str
    whatsapp_verify_token: str
    log_level: str = "INFO"


settings = Settings()  # type: ignore[call-arg]
