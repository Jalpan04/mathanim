import logging
from typing import List, Any
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langchain_community.chat_models import ChatOllama
from app.core.config import settings

logger = logging.getLogger(__name__)


class ResilientLLM:
    """
    Unified LLM runner that prioritizes cloud API if configured,
    and seamlessly falls back to local Ollama (GPU-accelerated) on errors or quota limits.
    """

    def __init__(self, temperature: float = 0.1):
        self.temperature = temperature
        self._primary_client = None
        self._primary_exhausted = False
        self._ollama_client = None
        self._init_clients()

    def _init_clients(self):
        # 1. Initialize local Ollama
        try:
            self._ollama_client = ChatOllama(
                model=settings.OLLAMA_MODEL,
                base_url=settings.OLLAMA_BASE_URL,
                temperature=self.temperature,
            )
        except Exception as e:
            logger.warning(f"Failed to initialize ChatOllama: {e}")

        # 2. Initialize primary API client if configured and key is present
        provider = settings.LLM_PROVIDER
        if provider != "ollama" and settings.OPENAI_API_KEY:
            try:
                from langchain_openai import ChatOpenAI
                kwargs = {
                    "model": settings.OPENAI_MODEL,
                    "api_key": settings.OPENAI_API_KEY,
                    "temperature": self.temperature,
                    "max_retries": 0,
                    "request_timeout": 15,
                }
                if settings.OPENAI_BASE_URL:
                    kwargs["base_url"] = settings.OPENAI_BASE_URL
                self._primary_client = ChatOpenAI(**kwargs)
            except Exception as e:
                logger.warning(f"Failed to initialize ChatOpenAI: {e}")

    def invoke(self, messages: List[BaseMessage] | str, **kwargs) -> Any:
        if isinstance(messages, str):
            messages = [HumanMessage(content=messages)]

        # Try primary API client first if available and not known to be exhausted
        if self._primary_client and not self._primary_exhausted and settings.LLM_PROVIDER != "ollama":
            try:
                return self._primary_client.invoke(messages, **kwargs)
            except Exception as e:
                err_msg = str(e).lower()
                if "insufficient_quota" in err_msg or "credit_balance_exhausted" in err_msg or "429" in err_msg or "invalid_api_key" in err_msg:
                    self._primary_exhausted = True
                    print(f"[LLM] Primary cloud API quota exhausted or unavailable. Switching to local GPU Ollama ({settings.OLLAMA_MODEL}).")
                else:
                    print(f"[LLM] Primary LLM call failed: {e}. Falling back to Ollama.")

        # Fallback to local Ollama
        if self._ollama_client:
            return self._ollama_client.invoke(messages, **kwargs)

        raise RuntimeError("No LLM client available. Ensure Ollama is running or configure an API key.")


def get_llm(temperature: float = 0.1) -> ResilientLLM:
    """Returns a configured ResilientLLM instance."""
    return ResilientLLM(temperature=temperature)
