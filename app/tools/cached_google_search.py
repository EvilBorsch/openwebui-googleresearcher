from typing import List, Dict, Any, Tuple
import time
from langchain_core.tools import tool
from .google_search import google_search as google_search_tool
from ..config import settings
from ..logging import logger


_CACHE: dict[Tuple[str, int], tuple[float, List[Dict[str, Any]]]] = {}


@tool("cached_google_search", return_direct=False)
def cached_google_search(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Return top N Google CSE results with TTL caching. Only one call should be used per research."""
    key = (query, max_results)
    now = time.time()
    ttl = settings.search_ttl_seconds
    logger.info(f"[search] query='{query}' max_results={max_results}")
    if key in _CACHE:
        ts, payload = _CACHE[key]
        if now - ts <= ttl:
            logger.info(f"[search] cache: hit age={int(now - ts)}s results={len(payload)}")
            return payload
        else:
            logger.info(f"[search] cache: expired age={int(now - ts)}s -> refresh")
    else:
        logger.info("[search] cache: miss -> perform Google CSE")
    results = google_search_tool.invoke({"query": query, "max_results": max_results})
    for idx, r in enumerate(results, start=1):
        logger.info(f"[search] {idx}. title='{r.get('title')}' url={r.get('link')}")
    _CACHE[key] = (now, results)
    return results
