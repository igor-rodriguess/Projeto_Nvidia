from app.core.startup_analysis_state import StartupAnalysisState
from app.db.startup_repository import persist_startup_discovery_result
from app.graph.startup_discovery_graph import startup_discovery_graph


def _initial_state(query: str) -> StartupAnalysisState:
    return {
        "query": query,
        "search_terms": [],
        "sources": [],
        "startups": [],
        "validated_startups": [],
        "nvidia_recommendations": [],
        "persistence": {},
        "attempt_count": 0,
        "errors": [],
    }


def run_startup_discovery_pipeline(query: str) -> StartupAnalysisState:
    result = startup_discovery_graph.invoke(_initial_state(query))
    result["persistence"] = persist_startup_discovery_result(result)
    return result


class StartupSearchPipeline:
    """Orchestrates the startup discovery pipeline via LangGraph."""

    async def run(self, query: str) -> StartupAnalysisState:
        return run_startup_discovery_pipeline(query)
