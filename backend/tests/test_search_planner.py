from app.agents.search_planner_agent import search_planner_agent
from app.core.startup_analysis_state import StartupAnalysisState


def test_search_planner_returns_required_search_variations():
    state: StartupAnalysisState = {"query": "healthtech IA Brasil"}

    result = search_planner_agent(state)

    search_terms = result["search_terms"]
    assert "healthtech IA Brasil startup Brasil" in search_terms
    assert "healthtech IA Brasil inteligência artificial" in search_terms
    assert "healthtech IA Brasil machine learning" in search_terms
    assert "healthtech IA Brasil site:startups.com.br" in search_terms
    assert "healthtech IA Brasil site:exame.com startups" in search_terms


def test_search_planner_increments_attempt_count():
    state: StartupAnalysisState = {"query": "startup fintech IA", "attempt_count": 0}

    result = search_planner_agent(state)

    assert result["attempt_count"] == 1


def test_search_planner_handles_empty_query():
    state: StartupAnalysisState = {"query": " ", "errors": []}

    result = search_planner_agent(state)

    assert result["search_terms"] == []
    assert result["attempt_count"] == 1
    assert result["errors"]
