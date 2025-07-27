import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Main application settings"""
    
    # Database settings
    database_url: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:postgres@localhost:5432/issues_tracker"
    )
    
    # Security settings
    jwt_secret: str = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS settings
    allowed_origins: list = ["http://localhost:5173", "http://localhost:3000"]
    
    # Redis settings
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # File upload settings
    upload_directory: str = "uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    
    # Environment
    railway_environment: Optional[str] = os.getenv("RAILWAY_ENVIRONMENT")
    
    # Google OAuth settings (from docker-compose.yml)
    google_client_id: Optional[str] = os.getenv("GOOGLE_CLIENT_ID", "your-google-client-id")
    google_client_secret: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET", "your-google-client-secret")
    
    # AI Settings
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()
