from typing import List, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl, Field


class ResearchRequest(BaseModel):
    query: str = Field(..., description="Research topic or question")
    instructions: Optional[str] = Field(None, description="Optional instructions or angle")
    max_search_results: int = Field(5, ge=1, le=5, description="Max Google results to fetch (<=5)")


class PageSection(BaseModel):
    heading: Optional[str] = None
    content: str


class ParsedPage(BaseModel):
    url: HttpUrl
    title: Optional[str] = None
    description: Optional[str] = None
    content_text: Optional[str] = None
    sections: Optional[List[PageSection]] = None
    links_followed: Optional[List[HttpUrl]] = None
    metadata: Optional[Dict[str, Any]] = None


class Citation(BaseModel):
    url: HttpUrl
    title: Optional[str] = None
    snippet: Optional[str] = None


class ResearchResult(BaseModel):
    topic: str
    summary: str
    citations: List[Citation]
    pages: List[ParsedPage]


__all__ = [
    "ResearchRequest",
    "ParsedPage",
    "PageSection",
    "Citation",
    "ResearchResult",
]
