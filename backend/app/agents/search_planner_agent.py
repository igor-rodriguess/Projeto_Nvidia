from app.core.startup_analysis_state import StartupAnalysisState


def search_planner_agent(state: StartupAnalysisState) -> StartupAnalysisState:
    query = state["query"]
    attempt_count = state.get("attempt_count", 0)

    base_terms = [
        query,
        f"{query} startup Brasil",
        f"{query} inteligência artificial",
        f"{query} machine learning",
    ]

    if attempt_count > 0:
        base_terms.extend([
            f"{query} site:startups.com.br",
            f"{query} site:exame.com startups",
            f"{query} site:startse.com",
        ])

    state["search_terms"] = base_terms
    state["attempt_count"] = attempt_count + 1

    return state 