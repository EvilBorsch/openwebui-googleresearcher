from bs4 import BeautifulSoup
from readability import Document
from typing import List, Tuple, Dict, Any
from urllib.parse import urljoin, urlparse


def extract_main_content(html: str) -> Tuple[str, Dict[str, Any]]:
    doc = Document(html)
    title = doc.short_title() or None
    summary_html = doc.summary(html_partial=True)
    soup = BeautifulSoup(summary_html, "lxml")
    text = soup.get_text("\n")
    return text, {"title": title}


def extract_links(html: str, base_url: str) -> List[str]:
    soup = BeautifulSoup(html, "lxml")
    base_host = urlparse(base_url).netloc
    unique: List[str] = []

    def _add(h: str) -> None:
        absolute = urljoin(base_url, h)
        host = urlparse(absolute).netloc
        if host != base_host:
            return
        if absolute not in unique:
            unique.append(absolute)

    for a in soup.find_all("a", href=True):
        href = a.get("href")
        if not href:
            continue
        if href.startswith("#"):
            continue
        if href.startswith("javascript:"):
            continue
        _add(href)
        if len(unique) >= 5:
            break

    return unique[:5]
