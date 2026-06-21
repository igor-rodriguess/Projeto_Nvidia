import pytest

from app.agents.data_extractor_agent import DataExtractorAgent
from app.core.startup_analysis_state import StartupAnalysisState


@pytest.fixture
def agent():
    return DataExtractorAgent()


def test_data_extractor_raises_not_implemented(agent):
    state: StartupAnalysisState = {
        "query": "startups brasileiras de saúde com IA",
        "raw_texts": ["Empresa X é uma startup de saúde que usa IA para diagnóstico."],
        "collected_sources": [{"url": "https://distrito.me/empresa-x", "title": "Empresa X"}],
    }
    with pytest.raises(NotImplementedError):
        agent.run(state)
