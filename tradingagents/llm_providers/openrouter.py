# TradingAgents/llm_providers/openrouter.py

import os
from typing import Any, Dict, Optional
from langchain_openai import ChatOpenAI
from pydantic import Field


class ChatOpenRouter(ChatOpenAI):
    """OpenRouter LLM wrapper that extends ChatOpenAI with OpenRouter-specific headers."""
    
    openrouter_site_url: Optional[str] = Field(default=None)
    openrouter_site_name: Optional[str] = Field(default=None)
    
    def __init__(
        self,
        model: str = "deepseek/deepseek-chat-v3-0324:free",
        openrouter_site_url: Optional[str] = None,
        openrouter_site_name: Optional[str] = None,
        **kwargs
    ):
        """Initialize OpenRouter client.
        
        Args:
            model: OpenRouter model name (e.g., "deepseek/deepseek-r1-0528:free")
            openrouter_site_url: Your site URL for rankings on openrouter.ai
            openrouter_site_name: Your site name for rankings on openrouter.ai
            **kwargs: Additional arguments passed to ChatOpenAI
        """
        # Set OpenRouter defaults
        kwargs.setdefault("base_url", "https://openrouter.ai/api/v1")
        kwargs.setdefault("api_key", os.getenv("OPENROUTER_API_KEY"))
        
        # Set OpenRouter-specific headers
        default_headers = {}
        if openrouter_site_url:
            default_headers["HTTP-Referer"] = openrouter_site_url
        if openrouter_site_name:
            default_headers["X-Title"] = openrouter_site_name
            
        if default_headers:
            kwargs.setdefault("default_headers", default_headers)
        
        super().__init__(model=model, **kwargs)
        
        self.openrouter_site_url = openrouter_site_url
        self.openrouter_site_name = openrouter_site_name

    @classmethod
    def from_config(cls, config: Dict[str, Any], model: str) -> "ChatOpenRouter":
        """Create ChatOpenRouter instance from config.
        
        Args:
            config: Configuration dictionary
            model: OpenRouter model name
            
        Returns:
            ChatOpenRouter instance
        """
        return cls(
            model=model,
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
            openrouter_site_url=config.get("openrouter_site_url"),
            openrouter_site_name=config.get("openrouter_site_name"),
        )


# Convenience functions for common OpenRouter models
def create_deepseek_reasoning_model(config: Dict[str, Any]) -> ChatOpenRouter:
    """Create DeepSeek reasoning model (deepseek-r1)."""
    return ChatOpenRouter.from_config(config, "deepseek/deepseek-r1-0528:free")


def create_deepseek_chat_model(config: Dict[str, Any]) -> ChatOpenRouter:
    """Create DeepSeek chat model (deepseek-chat-v3)."""
    return ChatOpenRouter.from_config(config, "deepseek/deepseek-chat-v3-0324:free")


def create_openrouter_model(config: Dict[str, Any], model_name: str) -> ChatOpenRouter:
    """Create any OpenRouter model."""
    return ChatOpenRouter.from_config(config, model_name)


# Common OpenRouter models mapping
OPENROUTER_MODELS = {
    # DeepSeek models (free)
    "deepseek-r1": "deepseek/deepseek-r1-0528:free",
    "deepseek-chat": "deepseek/deepseek-chat-v3-0324:free",
    
    # Meta models (free)
    "llama-3.1-8b": "meta-llama/llama-3.1-8b-instruct:free",
    "llama-3.2-3b": "meta-llama/llama-3.2-3b-instruct:free",
    
    # Google models (free)
    "gemma-7b": "google/gemma-7b-it:free",
    "gemma-2-9b": "google/gemma-2-9b-it:free",
    
    # Microsoft models (free)
    "phi-3-mini": "microsoft/phi-3-mini-128k-instruct:free",
    "phi-3-medium": "microsoft/phi-3-medium-128k-instruct:free",
    
    # Hugging Face models (free)
    "qwen-2.5-7b": "qwen/qwen-2.5-7b-instruct:free",
    "mistral-7b": "mistralai/mistral-7b-instruct:free",
}


def get_model_name(model_key: str) -> str:
    """Get OpenRouter model name from key."""
    return OPENROUTER_MODELS.get(model_key, model_key)
