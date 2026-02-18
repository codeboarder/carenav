"""Configuration settings for CareNav Florida backend."""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Azure OpenAI - East US 2
    azure_openai_endpoint: str = "https://ahfy26-resource.cognitiveservices.azure.com/"
    azure_openai_api_key: str = ""
    azure_openai_api_version: str = "2024-12-01-preview"
    
    # Model deployments
    model_gpt_5_2: str = "gpt-5.2"
    model_gpt_5_nano: str = "gpt-5-nano"
    model_embedding: str = "text-embedding-3-large"
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./carenav.db"
    
    # ChromaDB
    chroma_persist_directory: str = "./chroma_data"
    
    # App settings
    environment: str = "development"
    debug: bool = True
    
    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
