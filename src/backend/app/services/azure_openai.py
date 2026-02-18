"""
Azure OpenAI service for CareNav Florida.
Built by Gregory Katz and Rick Weyenberg
Code is as-is, open source
"""
import json
from typing import Optional
from openai import AsyncAzureOpenAI
from app.config import get_settings


class AzureOpenAIService:
    """Service for interacting with Azure OpenAI endpoints."""
    
    def __init__(self):
        settings = get_settings()
        self.client = AsyncAzureOpenAI(
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint,
        )
        self.model = settings.model_gpt_5_2
        self.fast_model = settings.model_gpt_5_nano
    
    async def chat_completion(
        self,
        messages: list[dict],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: Optional[dict] = None,
    ) -> dict:
        """Get a chat completion from Azure OpenAI."""
        kwargs = {
            "model": model or self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format:
            kwargs["response_format"] = response_format
        
        response = await self.client.chat.completions.create(**kwargs)
        return {
            "content": response.choices[0].message.content,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            "model": response.model,
        }
    
    async def chat_completion_json(
        self,
        messages: list[dict],
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> dict:
        """Get a JSON-formatted chat completion."""
        response = await self.chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )
        try:
            return json.loads(response["content"])
        except json.JSONDecodeError:
            return {"error": "Failed to parse JSON response", "raw": response["content"]}
    
    async def get_embedding(self, text: str) -> list[float]:
        """Get an embedding for text using Azure OpenAI."""
        settings = get_settings()
        response = await self.client.embeddings.create(
            model=settings.model_embedding,
            input=text,
        )
        return response.data[0].embedding


_service: Optional[AzureOpenAIService] = None


def get_azure_openai_service() -> AzureOpenAIService:
    """Get or create the Azure OpenAI service singleton."""
    global _service
    if _service is None:
        _service = AzureOpenAIService()
    return _service
