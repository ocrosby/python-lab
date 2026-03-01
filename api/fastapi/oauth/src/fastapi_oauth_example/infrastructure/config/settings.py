from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/fastapi_oauth"
    )
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15
    password_reset_token_expire_hours: int = 1
    email_verification_token_expire_hours: int = 24
    rate_limit_requests_per_minute: int = 5
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8080"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]
    allowed_hosts: list[str] = ["localhost", "127.0.0.1", "*.example.com"]
    gzip_minimum_size: int = 1000
    gzip_compression_level: int = 5


settings = Settings()
