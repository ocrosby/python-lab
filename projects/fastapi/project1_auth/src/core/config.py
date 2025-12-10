from pydantic import field_validator, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings with validation.
    
    Loads configuration from environment variables and .env file.
    All settings are validated on instantiation.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    database_url: str = Field(
        default="postgresql://project1:project1@localhost:5432/project1",
        description="PostgreSQL database URL"
    )
    
    postgres_db: str = Field(default="project1", description="PostgreSQL database name")
    postgres_user: str = Field(default="project1", description="PostgreSQL user")
    postgres_password: str = Field(default="project1", description="PostgreSQL password")
    
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT signing"
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=30,
        ge=1,
        le=1440,
        description="Access token expiration in minutes"
    )
    refresh_token_expire_days: int = Field(
        default=7,
        ge=1,
        le=90,
        description="Refresh token expiration in days"
    )
    
    db_pool_min_conn: int = Field(
        default=1,
        ge=1,
        description="Minimum database pool connections"
    )
    db_pool_max_conn: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum database pool connections"
    )
    
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )
    
    pythonunbuffered: str = Field(default="1", description="Python unbuffered mode")
    
    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is one of the allowed values."""
        allowed = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in allowed:
            raise ValueError(f'log_level must be one of {allowed}')
        return v.upper()
    
    @field_validator('secret_key')
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Validate secret key is not the default in production."""
        if v == "your-secret-key-change-in-production":
            import os
            if os.getenv('ENVIRONMENT', 'development') == 'production':
                raise ValueError('secret_key must be changed in production')
        return v
    
    @field_validator('db_pool_max_conn')
    @classmethod
    def validate_pool_size(cls, v: int, info) -> int:
        """Validate max connections is greater than min."""
        if 'db_pool_min_conn' in info.data and v < info.data['db_pool_min_conn']:
            raise ValueError('db_pool_max_conn must be >= db_pool_min_conn')
        return v


def get_settings() -> Settings:
    """
    Get application settings instance.
    
    Returns:
        Validated Settings instance
    """
    return Settings()
