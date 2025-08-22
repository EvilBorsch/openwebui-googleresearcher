from typing import Dict, Any, List
from urllib.parse import urljoin
from langchain_core.tools import tool
from ..utils.fetch import fetch_text
from ..utils.parse import extract_main_content, extract_links


@tool("research_page", return_direct=False)
async def research_page(url: str) -> Dict[str, Any]:
    """Fetch and parse a web page, extracting main content and following up to 5 in-site links."""
    html = await fetch_text(url)
    content_text, meta = extract_main_content(html)
    links = extract_links(html, url)

    followed: List[str] = []
    subpages: List[Dict[str, Any]] = []

    for href in links[:5]:
        absolute = urljoin(url, href)
        try:
            sub_html = await fetch_text(absolute)
            sub_text, sub_meta = extract_main_content(sub_html)
            subpages.append({
                "url": absolute,
                "title": sub_meta.get("title"),
                "content_text": sub_text,
            })
            followed.append(absolute)
        except Exception:
            continue

    return {
        "url": url,
        "title": meta.get("title"),
        "content_text": content_text,
        "subpages": subpages,
        "links_followed": followed,
    }
