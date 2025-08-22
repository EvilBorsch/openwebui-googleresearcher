import os
from langchain_openai import ChatOpenAI
from .config import settings


def make_llm() -> ChatOpenAI:
    os.environ["OPENAI_API_KEY"] = settings.openrouter_api_key
    os.environ["OPENAI_BASE_URL"] = settings.openrouter_base_url
    return ChatOpenAI(model=settings.openrouter_model, temperature=0.2, timeout=settings.llm_timeout_seconds)
