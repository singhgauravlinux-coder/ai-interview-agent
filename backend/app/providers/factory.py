from functools import lru_cache
from app.config import settings
from app.providers.base import AIProvider

@lru_cache(maxsize=4)
def get_ai_provider() -> AIProvider:
    provider = settings.ai_provider.lower().strip()
    if provider == "gemini":
        from app.providers.gemini import GeminiProvider
        return GeminiProvider()
    if provider == "openai":
        from app.providers.openai import OpenAIProvider
        return OpenAIProvider()
    raise ValueError(
        f"Unsupported AI_PROVIDER '{settings.ai_provider}'. "
        "Supported providers: gemini, openai."
    )

def clear_provider_cache():
    get_ai_provider.cache_clear()
