"""Services for CareNav Florida backend."""
from .azure_openai import AzureOpenAIService, get_azure_openai_service
from .llm_service import LLMProvider, get_llm_provider, reset_provider

# Note: KnowledgeBaseService is imported lazily to avoid loading ChromaDB on startup
# Use: from app.services.knowledge_base import get_knowledge_base_service

__all__ = [
    # Legacy Azure OpenAI service (kept as fallback)
    "AzureOpenAIService",
    "get_azure_openai_service",
    # New LLM abstraction layer (use this for new code)
    "LLMProvider",
    "get_llm_provider",
    "reset_provider",
]
