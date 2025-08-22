from typing import List, Dict, Any
import os
from langchain_community.utilities.google_search import GoogleSearchAPIWrapper
from langchain_core.tools import tool
from ..config import settings


def _make_wrapper() -> GoogleSearchAPIWrapper:
    os.environ["GOOGLE_API_KEY"] = settings.google_api_key
    os.environ["GOOGLE_CSE_ID"] = settings.google_cse_id
    return GoogleSearchAPIWrapper()


@tool("google_search", return_direct=False)
def google_search(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Search Google CSE and return up to top N results with title, link, and snippet."""
    wrapper = _make_wrapper()
    results = wrapper.results(query, max_results)
    pruned = []
    for r in results[:max_results]:
        pruned.append({
            "title": r.get("title"),
            "link": r.get("link"),
            "snippet": r.get("snippet") or r.get("snippet_highlighted_words"),
        })
    return pruned
