from typing import Any
import os
from langchain.agents import initialize_agent, AgentType
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from .config import settings
from .tools.google_search import google_search
from .tools.research_page import research_page
from .tools.research_web import research_web


def make_llm() -> ChatOpenAI:
    os.environ["OPENAI_API_KEY"] = settings.openrouter_api_key
    os.environ["OPENAI_BASE_URL"] = settings.openrouter_base_url
    return ChatOpenAI(model=settings.openrouter_model, temperature=0.2)


def make_agent() -> Any:
    # Prefer the merged tool to minimize calls and cost; keep granular tools as fallback utilities
    tools: list[BaseTool] = [research_web, google_search, research_page]
    llm = make_llm()
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=False,
        handle_parsing_errors=True,
        max_iterations=10,
    )
    return agent
