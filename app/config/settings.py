from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    chat_provider: str = "openai"
    chat_model: str = "gpt-4o-mini"
    chat_api_key: str
    chat_base_url: str | None = None
    chat_max_tokens: int = 1024
    embedding_provider: str = "openai"
    embedding_model: str = "text-embedding-3-small"
    embedding_api_key: str
    embedding_base_url: str | None = None
    embedding_dimensions: int = 1536
    chunk_strategy: str = "fixed"
    chunk_size: int = 500
    chunk_overlap: int = 50
    retrieval_top_k: int = 5
    retrieval_min_score: float | None = None
    retrieval_max_chunks: int = 5
    retrieval_max_context_tokens: int = 2000
    retrieval_encoding: str = "cl100k_base"
    whatsapp_token: str
    whatsapp_verify_token: str
    log_level: str = "INFO"
    log_format: str = "text"


settings = Settings()  # type: ignore[call-arg]
