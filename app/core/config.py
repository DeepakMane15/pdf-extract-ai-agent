from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = 'Company Backend Service'
    app_version: str = '1.0.0'
    debug: bool = True
    api_v1_prefix: str = '/api/v1'

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

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    @computed_field
    @property
    def sqlalchemy_database_uri(self) -> str:
        return (
            f'postgresql+psycopg://{self.postgres_user}:{self.postgres_password}'
            f'@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}'
        )


settings = Settings()
