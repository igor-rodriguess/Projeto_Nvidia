import pytest

from app.agents.source_collector_agent import SourceCollectorAgent
from app.core.startup_analysis_state import StartupAnalysisState


@pytest.fixture
def agent():
    return SourceCollectorAgent()


def test_source_collector_raises_not_implemented(agent):
    state: StartupAnalysisState = {
        "query": "startups brasileiras de saúde com IA",
        "search_terms": ["startup saúde IA Brasil"],
        "priority_sources": ["distrito.me"],
    }
    with pytest.raises(NotImplementedError):
        agent.run(state)
