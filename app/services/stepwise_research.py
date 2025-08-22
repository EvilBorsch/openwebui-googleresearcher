from typing import Dict, Any, List, Tuple
from langchain.agents import initialize_agent, AgentType
from langchain_core.tools import BaseTool
from ..llm import make_llm
from ..tools.cached_google_search import cached_google_search
from ..tools.fetch_page import fetch_page
from ..logging import logger
from ..observability.callbacks import ResearchLoggingHandler
from ..config import settings


MAX_STEPS = settings.agent_max_steps


def make_stepwise_agent() -> Any:
    tools: List[BaseTool] = [cached_google_search, fetch_page]
    llm = make_llm()
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=False,
        handle_parsing_errors=True,
        max_iterations=MAX_STEPS,
    )
    return agent


def run_stepwise_research(query: str, instructions: str | None, max_results: int = 5) -> Tuple[str, List[Dict[str, Any]], List[Dict[str, Any]]]:
    logger.info(f"[stepwise] start query='{query}' max_results={max_results}")
    if instructions:
        logger.info(f"[stepwise] instructions='{instructions}'")

    agent = make_stepwise_agent()

    system_prompt = (
        "You are a stepwise researcher. Strict rules: "
        "Use cached_google_search ONCE. Begin with the FIRST result. "
        "After each fetch_page, decide if the page already contains the answer. "
        "If it likely contains the answer but needs context, fetch a FEW in-site links (via fetch_page on those links). "
        "If it clearly does NOT contain the answer, move to the NEXT Google result. "
        f"Stop after at most {MAX_STEPS} total tool calls. "
        "Only rely on content you fetched. Finish with a concise grounded answer. "
        "For time/place-sensitive queries (e.g., movie showtimes, tickets, schedules in a city on a date), do NOT give generic disclaimers. "
        "Instead, escalate to the next result and parse multiple authoritative sources (ticketing and cinema listings) until you can provide an actionable answer or conclude unavailability."
    )

    q = query if not instructions else f"{query}\nInstructions: {instructions}"
    cb = ResearchLoggingHandler(trace=query[:60])
    result = agent.invoke(q + "\n" + system_prompt, config={"callbacks": [cb]})
    final_text: str = result["output"]
    logger.info(f"[stepwise] summary_len={len(final_text)}")

    results = cached_google_search.invoke({"query": query, "max_results": max_results})

    pages: List[Dict[str, Any]] = []
    for r in results[:3]:
        if not r.get("link"):
            continue
        try:
            logger.info(f"[stepwise] include result url={r['link']}")
            parsed = fetch_page.invoke({"url": r["link"]})
            if parsed:
                pages.append(parsed)
        except Exception as e:
            logger.warning(f"[stepwise] failed to parse page: {e}")

    citations: List[Dict[str, Any]] = []
    for idx, r in enumerate(results, start=1):
        url = r.get("link")
        if not url:
            continue
        logger.info(f"[stepwise] citation {idx}: {url}")
        citations.append({"url": url, "title": r.get("title"), "snippet": r.get("snippet")})

    return final_text, citations, pages
