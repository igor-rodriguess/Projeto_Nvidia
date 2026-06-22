from typing import List, Dict, Any
from app.core.startup_analysis_state import StartupAnalysisState

# ---------------------------------------------------------------------------
# Mock data – simulates what a real search API (SerpAPI, Google CSE, etc.)
# would return.  Replace _fetch_sources_for_term() with a real API call when
# ready to integrate.
# ---------------------------------------------------------------------------

_MOCK_SOURCES_DB: Dict[str, List[Dict[str, Any]]] = {
    "default": [
        {
            "title": "Startups brasileiras de tecnologia – panorama geral",
            "url": "https://startse.com/artigos/startups-brasil",
            "snippet": "Levantamento das principais startups de tecnologia no Brasil, com foco em IA e saúde digital.",
            "source_type": "public_search",
            "confidence": "low",
        },
        {
            "title": "Ranking das startups de IA no Brasil | Exame",
            "url": "https://exame.com/negocios/startups-ia-brasil",
            "snippet": "Conheça as startups brasileiras que lideram o uso de inteligência artificial em diferentes setores.",
            "source_type": "public_search",
            "confidence": "low",
        },
        {
            "title": "Ecossistema de inovação – startups.com.br",
            "url": "https://startups.com.br/ecossistema",
            "snippet": "Diretório completo de startups ativas no Brasil categorizadas por setor, estágio e tecnologia.",
            "source_type": "directory",
            "confidence": "low",
        },
    ]
}


def _fetch_sources_for_term(term: str) -> List[Dict[str, Any]]:
    """
    Returns mock sources for a given search term.

    TODO: replace this function body with a real API call, e.g.:
        response = serpapi.search({"q": term, "engine": "google", ...})
        return _parse_serpapi_response(response)
    """
    sources = []
    for base in _MOCK_SOURCES_DB["default"]:
        source = dict(base)
        source["title"] = f"{base['title']} – {term}"
        source["snippet"] = f"[Resultado para '{term}'] {base['snippet']}"
        sources.append(source)
    return sources


def source_collector_agent(state: StartupAnalysisState) -> StartupAnalysisState:
    """
    Executes the search strategy defined by search_planner_agent.
    Collects public information from websites, news and directories.

    Reads:  state["search_terms"]
    Writes: state["sources"]
    """
    search_terms: List[str] = state.get("search_terms", [])

    if not search_terms:
        state.setdefault("errors", []).append(
            "source_collector_agent: no search_terms found in state"
        )
        state["sources"] = []
        return state

    collected: List[Dict[str, Any]] = []
    seen_urls: set = set()

    for term in search_terms:
        for source in _fetch_sources_for_term(term):
            if source["url"] not in seen_urls:
                seen_urls.add(source["url"])
                collected.append(source)

    state["sources"] = collected
    return state
