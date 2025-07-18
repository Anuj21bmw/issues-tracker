from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database configuration - Railway provides DATABASE_URL automatically
    database_url: str = os.getenv(
        "DATABASE_URL", 
        # Fallback to local development database
        "postgresql://postgres:postgres@localhost:5432/issues_tracker"
    )
    
    # Redis configuration (optional for Railway)
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # JWT configuration
    jwt_secret: str = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # OAuth configuration (optional)
    google_client_id: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
    google_client_secret: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")
    
    # Railway specific configurations
    port: int = int(os.getenv("PORT", "8000"))
    railway_environment: str = os.getenv("RAILWAY_ENVIRONMENT", "development")
    
    # CORS settings for production
    allowed_origins: list = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://*.railway.app",
        "https://*.up.railway.app"
    ]
    
    class Config:
        env_file = ".env"

settings = Settings()