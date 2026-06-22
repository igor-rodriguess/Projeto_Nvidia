from app.core.startup_analysis_state import StartupAnalysisState


_SEARCH_VARIATIONS = [
    "startup Brasil",
    "inteligência artificial",
    "machine learning",
    "site:startups.com.br",
    "site:exame.com startups",
]


def _build_search_terms(query: str, attempt_count: int) -> list[str]:
    cleaned_query = query.strip()
    terms = [cleaned_query]

    for variation in _SEARCH_VARIATIONS:
        terms.append(f"{cleaned_query} {variation}")

    if attempt_count > 0:
        terms.extend(
            [
                f"{cleaned_query} startups brasileiras IA",
                f"{cleaned_query} empresas brasileiras machine learning",
            ]
        )

    return list(dict.fromkeys(term for term in terms if term))


def search_planner_agent(state: StartupAnalysisState) -> StartupAnalysisState:
    query = state.get("query", "")
    attempt_count = state.get("attempt_count", 0)

    if not query.strip():
        state.setdefault("errors", []).append("search_planner_agent: query is empty")
        state["search_terms"] = []
        state["attempt_count"] = attempt_count + 1
        return state

    state["search_terms"] = _build_search_terms(query, attempt_count)
    state["attempt_count"] = attempt_count + 1

    return state
