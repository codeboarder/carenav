"""Configuration settings for CareNav Florida backend."""
# Built by Gregory Katz and Rick Weyenberg
# Code is as-is, open source

from pydantic_settings import BaseSettings
from functools import lru_cache
from urllib.parse import quote_plus


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
    database_url: str = ""
    
    # ChromaDB
    chroma_persist_directory: str = "./chroma_data"
    
    # Azure SQL (optional if DATABASE_URL is provided directly)
    azure_sql_server: str = ""
    azure_sql_database: str = ""
    azure_sql_username: str = ""
    azure_sql_password: str = ""
    azure_sql_odbc_driver: str = "ODBC Driver 18 for SQL Server"
    azure_sql_encrypt: bool = True
    azure_sql_trust_server_certificate: bool = False
    
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

    def resolve_database_url(self) -> str:
        """Resolve database URL from DATABASE_URL or AZURE_SQL_* settings."""
        if self.database_url.strip():
            return self.database_url

        required = (
            self.azure_sql_server,
            self.azure_sql_database,
            self.azure_sql_username,
            self.azure_sql_password,
        )
        if all(required):
            encrypt = "yes" if self.azure_sql_encrypt else "no"
            trust = "yes" if self.azure_sql_trust_server_certificate else "no"
            return (
                "mssql+aioodbc://"
                f"{quote_plus(self.azure_sql_username)}:{quote_plus(self.azure_sql_password)}"
                f"@{self.azure_sql_server}/{self.azure_sql_database}"
                f"?driver={quote_plus(self.azure_sql_odbc_driver)}"
                f"&Encrypt={encrypt}&TrustServerCertificate={trust}"
            )

        return "sqlite+aiosqlite:///./carenav.db"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
