from typing import Dict, Any, List, Tuple
import time
from urllib.parse import urljoin
from langchain_core.tools import tool
from ..config import settings
from .google_search import google_search as google_search_tool
from ..utils.fetch import fetch_text
from ..utils.parse import extract_main_content, extract_links


_SEARCH_CACHE: Dict[Tuple[str, int], Tuple[float, List[Dict[str, Any]]]] = {}


def _get_cached_search(query: str, max_results: int) -> List[Dict[str, Any]]:
    key = (query, max_results)
    now = time.time()
    ttl = settings.search_ttl_seconds
    cached = _SEARCH_CACHE.get(key)
    if cached:
        ts, payload = cached
        if now - ts <= ttl:
            return payload
    results = google_search_tool.invoke({"query": query, "max_results": max_results})
    _SEARCH_CACHE[key] = (now, results)
    return results


@tool("research_web", return_direct=False)
async def research_web(query: str, max_results: int = 5) -> Dict[str, Any]:
    """Perform a single TTL-cached web search; parse the first result thoroughly.
    If first page lacks an answer, escalate to parse additional top results; only then follow in-site links."""
    results = _get_cached_search(query, max_results)
    if not results:
        return {"query": query, "results": [], "pages": []}

    pages: List[Dict[str, Any]] = []

    async def parse_single(url: str) -> Dict[str, Any]:
        html = await fetch_text(url)
        content_text, meta = extract_main_content(html)
        links = extract_links(html, url)
        return {"url": url, "title": meta.get("title"), "content_text": content_text, "links": links}

    # Parse first result
    first_url = results[0].get("link")
    if first_url:
        first_parsed = await parse_single(first_url)
        pages.append(first_parsed)

    # Heuristic: if first page content is short or non-informative, escalate to next results
    def lacks_answer(text: str) -> bool:
        if not text:
            return True
        # Short content heuristic
        if len(text) < 800:
            return True
        return False

    need_escalation = True
    if pages and not lacks_answer(pages[0].get("content_text", "")):
        need_escalation = False

    if need_escalation:
        for r in results[1:]:
            url = r.get("link")
            if not url:
                continue
            try:
                parsed = await parse_single(url)
                pages.append(parsed)
                if not lacks_answer(parsed.get("content_text", "")):
                    break
            except Exception:
                continue

    # Optional: For the final chosen page(s), follow a few in-site links to enrich
    enriched: List[Dict[str, Any]] = []
    for p in pages[:2]:  # limit enrichment cost
        try:
            subpages: List[Dict[str, Any]] = []
            for href in p.get("links", [])[:5]:
                abs_url = urljoin(p["url"], href)
                try:
                    sub_html = await fetch_text(abs_url)
                    sub_text, sub_meta = extract_main_content(sub_html)
                    subpages.append({
                        "url": abs_url,
                        "title": sub_meta.get("title"),
                        "content_text": sub_text,
                    })
                except Exception:
                    continue
            enriched.append({
                "url": p["url"],
                "title": p.get("title"),
                "content_text": p.get("content_text"),
                "subpages": subpages,
            })
        except Exception:
            enriched.append(p)

    return {"query": query, "results": results, "pages": enriched}
