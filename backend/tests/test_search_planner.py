from app.agents.search_planner_agent import search_planner_agent
from app.core.startup_analysis_state import StartupAnalysisState


def test_search_planner_returns_search_terms():
    state: StartupAnalysisState = {"query": "startups brasileiras de saúde com IA"}
    result = search_planner_agent(state)
    assert "search_terms" in result
    assert len(result["search_terms"]) > 0


def test_search_planner_increments_attempt_count():
    state: StartupAnalysisState = {"query": "startup fintech IA", "attempt_count": 0}
    result = search_planner_agent(state)
    assert result["attempt_count"] == 1
