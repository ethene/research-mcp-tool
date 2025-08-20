"""OpenRouter API client for making requests."""

import httpx
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class OpenRouterClient:
    """Client for interacting with OpenRouter API."""
    
    def __init__(self, api_key: str, base_url: str = "https://openrouter.ai/api/v1"):
        """Initialize OpenRouter client."""
        if not api_key:
            raise ValueError("OpenRouter API key is required")
        
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/ethene/research-mcp-tool",
                "X-Title": "Research MCP Tool"
            },
            timeout=60.0
        )
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def list_models(self) -> Dict[str, Any]:
        """Get list of available models from OpenRouter."""
        try:
            response = await self.client.get(f"{self.base_url}/models")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch models: {e}")
            raise
    
    async def chat_completion(
        self, 
        model: str, 
        messages: List[Dict[str, str]], 
        **kwargs
    ) -> Dict[str, Any]:
        """Generate chat completion using specified model."""
        payload = {
            "model": model,
            "messages": messages,
            **kwargs
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Chat completion failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    logger.error(f"Error details: {error_detail}")
                except:
                    logger.error(f"Raw error response: {e.response.text}")
            raise