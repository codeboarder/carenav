"""
LLM Service Abstraction Layer
==============================
Built by Gregory Katz and Rick Weyenberg
Code is as-is, open source

This module abstracts all LLM interactions so they can be swapped
between Azure OpenAI (current) and GitHub Copilot SDK (target).

Gregory: To integrate the Copilot SDK, replace the AzureOpenAIProvider
class with a CopilotSDKProvider class that uses @github/copilot-sdk.

USAGE:
    from app.services.llm_service import get_llm_provider
    
    provider = get_llm_provider()
    response = await provider.chat_completion(messages)
    
TO SWITCH PROVIDERS:
    Change the `provider` variable in get_llm_provider() from "azure" to "copilot_sdk"
"""

import json
from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional, Dict, Any, List


class LLMProvider(ABC):
    """
    Base interface for LLM providers.
    
    All LLM providers must implement these methods to ensure
    consistent behavior across Azure OpenAI and GitHub Copilot SDK.
    """
    
    @abstractmethod
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Send a chat completion request.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens in response
            response_format: Optional format specification (e.g., {"type": "json_object"})
            
        Returns:
            Dict with 'content', 'usage', and 'model' keys
        """
        pass
    
    @abstractmethod
    async def chat_completion_json(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> Dict[str, Any]:
        """
        Send a chat completion request expecting JSON response.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys
            temperature: Sampling temperature (lower for more deterministic JSON)
            max_tokens: Maximum tokens in response
            
        Returns:
            Parsed JSON dict from the response
        """
        pass
    
    @abstractmethod
    async def get_embedding(self, text: str) -> List[float]:
        """
        Get an embedding vector for text.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        pass
    
    async def chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """
        Stream a chat completion response.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys
            temperature: Sampling temperature (0.0-1.0)
            
        Yields:
            String chunks of the response
        """
        raise NotImplementedError("Streaming not implemented for this provider")


class AzureOpenAIProvider(LLMProvider):
    """
    Azure OpenAI implementation - DO NOT DELETE.
    
    This is the current working implementation that uses Azure OpenAI endpoints.
    It serves as the fallback when the Copilot SDK is not available.
    """
    
    def __init__(self):
        from openai import AsyncAzureOpenAI
        from app.config import get_settings
        
        settings = get_settings()
        self.client = AsyncAzureOpenAI(
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint,
        )
        self.model = settings.model_gpt_5_2
        self.fast_model = settings.model_gpt_5_nano
        self.embedding_model = settings.model_embedding
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Send a chat completion request to Azure OpenAI."""
        kwargs = {
            "model": self.model,
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
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> Dict[str, Any]:
        """Get a JSON-formatted chat completion from Azure OpenAI."""
        response = await self.chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )
        try:
            return json.loads(response["content"])
        except json.JSONDecodeError:
            return {"error": "Failed to parse JSON response", "raw": response["content"]}
    
    async def get_embedding(self, text: str) -> List[float]:
        """Get an embedding for text using Azure OpenAI."""
        response = await self.client.embeddings.create(
            model=self.embedding_model,
            input=text,
        )
        return response.data[0].embedding
    
    async def chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """Stream a chat completion response from Azure OpenAI."""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            stream=True,
        )
        async for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class CopilotSDKProvider(LLMProvider):
    """
    PLACEHOLDER for GitHub Copilot SDK integration.
    Gregory will implement this locally in VS Code.
    
    The implementation will:
    1. Import CopilotClient from @github/copilot-sdk (via Node.js subprocess or bridge)
    2. Create a session with the desired model
    3. Register custom tools (the 6 agents) with the session
    4. Send prompts and return responses
    
    Since the SDK is Node.js and the backend is Python, options are:
    a) Use a Node.js sidecar process that the Python backend calls via HTTP
    b) Rewrite the backend service layer in Node.js
    c) Use the Copilot CLI in server mode and call it via JSON-RPC from Python
    
    Option (c) is recommended - the CLI runs as a server, and Python sends
    JSON-RPC messages directly. No Node.js wrapper needed.
    
    IMPLEMENTATION STEPS FOR GREGORY:
    
    1. Install the Copilot CLI:
       npm install -g @github/copilot-cli
    
    2. Start the CLI in server mode:
       copilot-cli serve --port 3000
    
    3. Implement the methods below to call the CLI via HTTP/JSON-RPC:
       - POST /chat for chat completions
       - POST /embed for embeddings
    
    4. Register the MCP servers as tools:
       - medicaid_server.py -> check_medicaid_eligibility, etc.
       - va_benefits_server.py -> check_va_eligibility, etc.
       - facility_search_server.py -> search_facilities, etc.
       - document_rag_server.py -> search_documents, etc.
    
    5. Change get_llm_provider() to return CopilotSDKProvider()
    """
    
    def __init__(self):
        # TODO: Gregory - Initialize connection to Copilot CLI server
        # self.cli_url = "http://localhost:3000"
        # self.session_id = None
        raise NotImplementedError(
            "CopilotSDKProvider is a placeholder. "
            "Gregory will implement this locally using the GitHub Copilot SDK."
        )
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        TODO: Gregory - Implement using Copilot CLI
        
        Example implementation:
        
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.cli_url}/chat",
                json={
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "tools": self._get_registered_tools(),
                }
            )
            return response.json()
        """
        raise NotImplementedError("CopilotSDKProvider.chat_completion not implemented")
    
    async def chat_completion_json(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> Dict[str, Any]:
        """TODO: Gregory - Implement using Copilot CLI with JSON mode"""
        raise NotImplementedError("CopilotSDKProvider.chat_completion_json not implemented")
    
    async def get_embedding(self, text: str) -> List[float]:
        """TODO: Gregory - Implement using Copilot CLI or Azure AI Search"""
        raise NotImplementedError("CopilotSDKProvider.get_embedding not implemented")
    
    def _get_registered_tools(self) -> List[Dict]:
        """
        Return the list of MCP tools registered with the Copilot session.
        
        These correspond to the MCP servers defined in mcp.json:
        - medicaid: check_medicaid_eligibility, get_medicaid_rules, etc.
        - va_benefits: check_va_eligibility, calculate_va_benefit, etc.
        - facility_search: search_facilities, compare_facilities, etc.
        - document_rag: search_documents, get_document, etc.
        """
        return [
            {
                "name": "check_medicaid_eligibility",
                "description": "Check Florida Medicaid ICP eligibility based on assets and income",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "assets": {"type": "number", "description": "Total countable assets in dollars"},
                        "income": {"type": "number", "description": "Monthly income in dollars"},
                        "marital_status": {"type": "string", "enum": ["single", "married", "widowed"]},
                    },
                    "required": ["assets", "income"],
                },
            },
            {
                "name": "check_va_eligibility",
                "description": "Check VA Aid & Attendance eligibility",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "is_veteran": {"type": "boolean"},
                        "is_spouse_of_veteran": {"type": "boolean"},
                        "wartime_service": {"type": "boolean"},
                        "veteran_deceased": {"type": "boolean"},
                    },
                    "required": ["wartime_service"],
                },
            },
            {
                "name": "search_facilities",
                "description": "Search for care facilities in Florida",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "zip_code": {"type": "string"},
                        "care_level": {"type": "string", "enum": ["AL", "MC", "SNF"]},
                        "medicaid_required": {"type": "boolean"},
                        "max_distance_miles": {"type": "number"},
                    },
                    "required": ["zip_code", "care_level"],
                },
            },
            {
                "name": "search_documents",
                "description": "Search patient documents using RAG",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "patient_id": {"type": "integer"},
                        "category": {"type": "string"},
                    },
                    "required": ["query", "patient_id"],
                },
            },
        ]


# Singleton instance
_provider: Optional[LLMProvider] = None


def get_llm_provider() -> LLMProvider:
    """
    Returns the active LLM provider.
    
    IMPORTANT: Change 'azure' to 'copilot_sdk' after SDK integration.
    
    This is the ONE LINE Gregory needs to change to switch providers.
    """
    global _provider
    
    if _provider is not None:
        return _provider
    
    # ============================================================
    # PROVIDER SELECTION - Gregory: Change this to switch providers
    # ============================================================
    provider_type = "azure"  # Options: "azure", "copilot_sdk"
    # ============================================================
    
    if provider_type == "azure":
        _provider = AzureOpenAIProvider()
    elif provider_type == "copilot_sdk":
        _provider = CopilotSDKProvider()
    else:
        raise ValueError(f"Unknown provider type: {provider_type}")
    
    return _provider


def reset_provider():
    """Reset the provider singleton (useful for testing)."""
    global _provider
    _provider = None
