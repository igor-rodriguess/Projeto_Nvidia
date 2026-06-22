from datetime import datetime, timezone
from typing import Any, Dict, List

from app.core.startup_analysis_state import StartupAnalysisState


DEFAULT_RESULTS_PER_TERM = 3
MAX_TOTAL_SOURCES = 20


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


def _normalize_result(result: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "title": result.get("title", "").strip(),
        "url": result.get("href", result.get("url", "")).strip(),
        "snippet": result.get("body", result.get("snippet", "")).strip(),
        "source_type": "public_search",
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

        for result in results:
            source = _normalize_result(result)
            url = source.get("url", "")
            if not url or url in seen_urls:
                continue

            seen_urls.add(url)
            collected.append(source)

            if len(collected) >= MAX_TOTAL_SOURCES:
                state["sources"] = collected
                return state

    state["sources"] = collected
    return state
