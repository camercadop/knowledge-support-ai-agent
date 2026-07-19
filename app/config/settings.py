from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    openai_api_key: str
    whatsapp_token: str
    whatsapp_verify_token: str


settings = Settings()  # type: ignore[call-arg]
