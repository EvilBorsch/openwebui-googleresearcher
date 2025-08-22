from typing import Dict, Any
from langchain_core.tools import tool
from ..utils.fetch import fetch_text_sync
from ..utils.parse import extract_main_content, extract_links
from ..logging import logger


@tool("fetch_page", return_direct=False)
def fetch_page(url: str) -> Dict[str, Any]:
    """Fetch a URL and return extracted content and in-site links."""
    logger.info(f"[fetch] url={url}")
    html = fetch_text_sync(url)
    content_text, meta = extract_main_content(html)
    links = extract_links(html, url)
    title = meta.get("title")
    logger.info(f"[fetch] parsed title='{title}' content_len={len(content_text) if content_text else 0} links={len(links)}")
    return {
        "url": url,
        "title": title,
        "content_text": content_text,
        "links": links,
    }
