from datetime import datetime, timezone
from typing import Any, Dict, List
from urllib.parse import urlparse

from app.core.startup_analysis_state import StartupAnalysisState


DEFAULT_RESULTS_PER_TERM = 3
MAX_TOTAL_SOURCES = 20


def _source_domain(url: str) -> str:
    parsed = urlparse(url)
    return parsed.netloc.lower().replace("www.", "")


def _is_valid_public_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _search_duckduckgo(term: str, max_results: int) -> List[Dict[str, Any]]:
    from ddgs import DDGS

    with DDGS() as ddgs:
        return list(
            ddgs.text(
                term,
                region="br-pt",
                safesearch="moderate",
                max_results=max_results,
            )
        )


def _normalize_result(
    result: Dict[str, Any],
    search_term: str | None = None,
    rank: int | None = None,
) -> Dict[str, Any]:
    url = result.get("href", result.get("url", "")).strip()
    return {
        "title": result.get("title", "").strip(),
        "url": url,
        "snippet": result.get("body", result.get("snippet", "")).strip(),
        "source_type": "public_search",
        "source_domain": _source_domain(url),
        "search_term": search_term,
        "search_rank": rank,
        "collected_at": datetime.now(timezone.utc).isoformat(),
    }


def source_collector_agent(state: StartupAnalysisState) -> StartupAnalysisState:
    search_terms: List[str] = state.get("search_terms", [])

    if not search_terms:
        state.setdefault("errors", []).append(
            "source_collector_agent: no search_terms found in state"
        )
        state["sources"] = []
        return state

    collected: List[Dict[str, Any]] = []
    seen_urls: set[str] = set()

    for term in search_terms:
        try:
            results = _search_duckduckgo(term, DEFAULT_RESULTS_PER_TERM)
        except Exception as exc:
            state.setdefault("errors", []).append(
                f"source_collector_agent: failed to search '{term}': {exc}"
            )
            continue

        for rank, result in enumerate(results, start=1):
            source = _normalize_result(result, search_term=term, rank=rank)
            url = source.get("url", "")
            if not _is_valid_public_url(url) or url in seen_urls:
                continue

            seen_urls.add(url)
            collected.append(source)

            if len(collected) >= MAX_TOTAL_SOURCES:
                state["sources"] = collected
                return state

    state["sources"] = collected
    return state
