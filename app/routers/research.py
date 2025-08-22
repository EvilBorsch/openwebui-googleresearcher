from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from ..schemas import ResearchRequest, ResearchResult, Citation, ParsedPage
from ..logging import setup_logging, logger

router = APIRouter()
setup_logging()


@router.post(
    "/research",
    response_model=ResearchResult,
    summary="Web research ONLY (use for: search/поищи/изучи/актуальная информация)",
    description=(
        "Use this tool ONLY for web research that requires live, up-to-date information (news, tickets, prices, schedules, current facts) "
        "or when the user explicitly requests browsing/searching the web.\n\n"
        "Positive triggers (English): search, browse, investigate, use web, up-to-date/current info, tickets, price, schedule, news.\n"
        "Положительные триггеры (RU): поищи, найди, изучи, используй актуальную/свежую информацию, билеты, цена, расписание, новости.\n\n"
        "Do NOT use for: subjective/opinion or preference questions (e.g., \"что лучше пицца или суши?\"), brainstorming, coding/math without needing the web, general knowledge that does not require recency, translation, or summarizing text already provided. "
        "If the request does not clearly ask for web search or up-to-date info, do not call this tool.\n\n"
        "Multiple calls are OK and encouraged if uncertain: This tool is idempotent and caches Google search results (TTL). "
        "If the answer seems incomplete/uncertain, CALL THIS TOOL AGAIN with higher \"parse_top_n\" and \"max_iterations\" and optionally \"force_escalate\".\n"
        "Example follow-ups: \n"
        "- Call 1: { query } -> if uncertain\n"
        "- Call 2: { query, parse_top_n: 4, max_iterations: 8, force_escalate: true } -> if still uncertain\n"
        "- Call 3: { query, parse_top_n: 5, max_iterations: 10, force_escalate: true }\n\n"
        "Behavior: performs one TTL-cached Google search, parses top-N results (configurable), selectively deepens via in-site links, and moves to the next result only if needed. "
        "Returns a grounded summary with citations and structured pages to avoid hallucinations."
    ),
)
async def research_endpoint(payload: ResearchRequest) -> ResearchResult:
    try:
        logger.info(f"[request] /research query='{payload.query}' max_results={payload.max_search_results}")
        if payload.instructions:
            logger.info(f"[request] instructions='{payload.instructions}'")

        from ..services.stepwise_research import run_stepwise_research
        summary_text, citations_raw, pages_raw, continuation = run_stepwise_research(
            query=payload.query,
            instructions=payload.instructions,
            max_results=payload.max_search_results,
            parse_top_n=payload.parse_top_n,
            max_iterations=payload.max_iterations,
            force_escalate=payload.force_escalate,
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
            continuation=continuation or None,
        )
    except Exception as e:
        logger.exception("research_endpoint error")
        raise HTTPException(status_code=500, detail=str(e))
