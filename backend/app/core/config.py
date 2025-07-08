from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@localhost:5432/issues_tracker"
    redis_url: str = "redis://localhost:6379"
    jwt_secret: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings()