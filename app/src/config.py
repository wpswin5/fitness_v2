"""
Application Configuration
"""
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Settings
    API_TITLE: str = "Fitness API"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database Settings
    DB_SERVER: str = ""
    DB_PORT: int = 1433
    DB_NAME: str = ""
    DB_USER: str = ""
    DB_PASSWORD: str = ""
    
    # Azure Settings
    AZURE_SUBSCRIPTION_ID: str = ""
    AZURE_RESOURCE_GROUP: str = ""
    
    # CORS Settings
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Connection string
    @property
    def DATABASE_URL(self) -> str:
        """Construct database connection string"""
        return f"mssql+pyodbc://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_SERVER}:{self.DB_PORT}/{self.DB_NAME}?driver=ODBC+Driver+17+for+SQL+Server"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
