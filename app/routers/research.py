from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from ..schemas import ResearchRequest, ResearchResult, Citation, ParsedPage
from ..logging import setup_logging, logger

router = APIRouter()
setup_logging()


@router.post(
    "/research",
    response_model=ResearchResult,
    summary="Web research (search / поищи / изучи using current web information)",
    description=(
        "Perform stepwise web research using live web search and page parsing. "
        "Use this tool when asked to: search, find, browse, investigate, use up-to-date/current information; "
        "or in Russian: поищи, найди, изучи, используй актуальную/текущую информацию. "
        "The tool runs a single TTL-cached Google search, parses the first result, selectively deepens via in-site links, "
        "and moves to the next result if needed. Returns a grounded summary with citations and structured pages to avoid hallucinations."
    ),
)
async def research_endpoint(payload: ResearchRequest) -> ResearchResult:
    try:
        logger.info(f"[request] /research query='{payload.query}' max_results={payload.max_search_results}")
        if payload.instructions:
            logger.info(f"[request] instructions='{payload.instructions}'")

        from ..services.stepwise_research import run_stepwise_research
        summary_text, citations_raw, pages_raw = run_stepwise_research(
            query=payload.query,
            instructions=payload.instructions,
            max_results=payload.max_search_results,
        )

        citations: List[Citation] = [
            Citation(url=c.get("url"), title=c.get("title"), snippet=c.get("snippet")) for c in citations_raw
            if c.get("url")
        ]

        pages: List[ParsedPage] = []
        for p in pages_raw:
            pages.append(ParsedPage(
                url=p.get("url"),
                title=p.get("title"),
                content_text=p.get("content_text"),
                links_followed=p.get("links"),
                metadata=None,
            ))

        logger.info(f"[response] citations={len(citations)} pages={len(pages)} summary_len={len(summary_text)}")
        return ResearchResult(
            topic=payload.query,
            summary=summary_text,
            citations=citations,
            pages=pages,
        )
    except Exception as e:
        logger.exception("research_endpoint error")
        raise HTTPException(status_code=500, detail=str(e))
