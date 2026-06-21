import pytest

from app.agents.search_planner_agent import SearchPlannerAgent
from app.core.startup_analysis_state import StartupAnalysisState


@pytest.fixture
def agent():
    return SearchPlannerAgent()


def test_search_planner_raises_not_implemented(agent):
    state: StartupAnalysisState = {"query": "startups brasileiras de saúde com IA"}
    with pytest.raises(NotImplementedError):
        agent.run(state)
