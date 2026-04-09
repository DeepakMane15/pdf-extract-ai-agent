from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = 'Company Backend Service'
    app_version: str = '1.0.0'
    debug: bool = True
    api_v1_prefix: str = '/api/v1'
    # Comma-separated origins for browser clients (e.g. Vite on :5173)
    cors_origins: str = 'http://localhost:5173,http://127.0.0.1:5173'

    postgres_host: str = 'localhost'
    postgres_port: int = 5432
    postgres_user: str = 'postgres'
    postgres_password: str = 'postgres'
    postgres_db: str = 'mydb'

    jwt_secret_key: str = 'change-me-in-production'
    jwt_algorithm: str = 'HS256'
    access_token_expire_minutes: int = 30

    seed_admin_email: str | None = None
    seed_admin_password: str | None = None
    seed_admin_full_name: str | None = None

    pdf_upload_dir: str = 'uploads/pdfs'
    max_pdf_upload_bytes: int = 20 * 1024 * 1024  # 20 MiB

    chunk_size_chars: int = 512
    chunk_overlap_chars: int = 64

    openai_api_key: str | None = None
    # Optional separate secret for encrypting per-user OpenAI keys (defaults to jwt_secret_key).
    openai_user_key_secret: str | None = None
    openai_embedding_model: str = 'text-embedding-3-small'
    openai_embedding_batch_size: int = 16
    openai_embedding_max_retries: int = 6

    openai_chat_model: str = 'gpt-4o-mini'
    openai_chat_temperature: float = 0.3
    openai_chat_max_tokens: int = 1024

    cohere_api_key: str | None = None
    cohere_rerank_model: str = 'rerank-english-v3.0'
    retrieval_vector_pool_size: int = 20

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    @computed_field
    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(',') if o.strip()]

    @computed_field
    @property
    def sqlalchemy_database_uri(self) -> str:
        return (
            f'postgresql+psycopg://{self.postgres_user}:{self.postgres_password}'
            f'@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}'
        )


settings = Settings()
