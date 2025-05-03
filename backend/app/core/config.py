from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings using environment variables."""
    
    # API settings
    api_title: str = "Cre8rFlow - NLP Video Editor API"
    api_description: str = "Backend API for Cre8rFlow NLP Video Editor"
    api_version: str = "1.0.0"
    
    # OpenAI settings
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    
    # Supabase settings
    supabase_url: str = Field(..., env="SUPABASE_URL")
    supabase_key: str = Field(..., env="SUPABASE_KEY")
    supabase_jwt_secret: str = Field(..., env="SUPABASE_JWT_SECRET")
    
    # Database settings
    postgres_user: str = Field(..., env="POSTGRES_USER")
    postgres_password: str = Field(..., env="POSTGRES_PASSWORD")
    postgres_host: str = Field(..., env="POSTGRES_HOST")
    postgres_port: int = Field(5432, env="POSTGRES_PORT")
    postgres_db: str = Field(..., env="POSTGRES_DB")
    
    # Redis settings
    redis_url: str = Field("redis://redis:6379", env="REDIS_URL")
    
    # Rate limiting
    command_rate_limit: int = Field(30, env="COMMAND_RATE_LIMIT")
    
    # Cors settings
    cors_origins: list[str] = Field(
        ["*"], env="CORS_ORIGINS"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings() 