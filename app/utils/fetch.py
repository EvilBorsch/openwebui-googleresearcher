import httpx
from typing import Optional
from ..config import settings


async def fetch_text(url: str, timeout: Optional[int] = None) -> str:
    timeout_seconds = timeout or settings.request_timeout_seconds
    headers = {"User-Agent": settings.user_agent}
    async with httpx.AsyncClient(timeout=timeout_seconds, headers=headers, follow_redirects=True) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.text


def fetch_text_sync(url: str, timeout: Optional[int] = None) -> str:
    timeout_seconds = timeout or settings.request_timeout_seconds
    headers = {"User-Agent": settings.user_agent}
    with httpx.Client(timeout=timeout_seconds, headers=headers, follow_redirects=True) as client:
        resp = client.get(url)
        resp.raise_for_status()
        return resp.text
