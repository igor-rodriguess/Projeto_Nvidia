from app.core.startup_analysis_state import StartupAnalysisState
from app.graph.startup_discovery_graph import startup_discovery_graph


def _initial_state(query: str) -> StartupAnalysisState:
    return {
        "query": query,
        "search_terms": [],
        "sources": [],
        "startups": [],
        "attempt_count": 0,
        "errors": [],
    }


def run_startup_discovery_pipeline(query: str) -> StartupAnalysisState:
    return startup_discovery_graph.invoke(_initial_state(query))


class StartupSearchPipeline:
    """Orchestrates the startup discovery pipeline via LangGraph."""

    async def run(self, query: str) -> StartupAnalysisState:
        return run_startup_discovery_pipeline(query)
