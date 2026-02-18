"""Configuration settings for CareNav Florida backend."""
# Built by Gregory Katz and Rick Weyenberg
# Code is as-is, open source

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Azure OpenAI - East US 2
    azure_openai_endpoint: str = ""
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
    
    # ============================================================
    # AZURE SQL — Rick: Uncomment after provisioning
    # ============================================================
    # azure_sql_server: str = ""
    # azure_sql_database: str = ""
    # azure_sql_username: str = ""
    # azure_sql_password: str = ""
    
    # ============================================================
    # AZURE AI SEARCH — Rick: Uncomment after provisioning
    # ============================================================
    # azure_search_endpoint: str = ""
    # azure_search_api_key: str = ""
    # azure_search_index: str = "carenav-documents"
    
    # ============================================================
    # FOUNDRY IQ — Rick: Uncomment after creating knowledge base
    # ============================================================
    # foundry_iq_knowledge_base_id: str = ""
    # azure_ai_foundry_endpoint: str = ""
    # azure_ai_foundry_api_key: str = ""
    
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
