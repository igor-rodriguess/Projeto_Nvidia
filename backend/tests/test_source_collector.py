import pytest

from app.agents.source_collector_agent import source_collector_agent
from app.core.startup_analysis_state import StartupAnalysisState

# ---------------------------------------------------------------------------
# Meta: dado um state com search_terms,
#       quando o Source Collector rodar,
#       então ele deve adicionar sources ao state.
# ---------------------------------------------------------------------------


def test_source_collector_adds_sources_to_state():
    state: StartupAnalysisState = {
        "query": "startups brasileiras de saúde com IA",
        "search_terms": ["healthtech IA Brasil", "healthtech IA Brasil startup Brasil"],
    }
    result = source_collector_agent(state)

    assert "sources" in result
    assert isinstance(result["sources"], list)
    assert len(result["sources"]) > 0


def test_source_collector_source_has_required_fields():
    state: StartupAnalysisState = {
        "query": "fintech IA",
        "search_terms": ["fintech IA Brasil"],
    }
    result = source_collector_agent(state)

    required_fields = {"title", "url", "snippet", "source_type", "confidence"}
    for source in result["sources"]:
        assert required_fields.issubset(source.keys()), (
            f"Source is missing fields: {required_fields - source.keys()}"
        )


def test_source_collector_no_duplicate_urls():
    state: StartupAnalysisState = {
        "query": "edtech",
        "search_terms": ["edtech IA Brasil", "edtech IA Brasil startup"],
    }
    result = source_collector_agent(state)

    urls = [s["url"] for s in result["sources"]]
    assert len(urls) == len(set(urls)), "Duplicate URLs found in sources"


def test_source_collector_empty_search_terms_returns_empty_sources():
    state: StartupAnalysisState = {
        "query": "qualquer coisa",
        "search_terms": [],
    }
    result = source_collector_agent(state)

    assert result["sources"] == []
    assert len(result.get("errors", [])) > 0


def test_source_collector_preserves_existing_state_fields():
    state: StartupAnalysisState = {
        "query": "agritech",
        "search_terms": ["agritech IA"],
        "attempt_count": 2,
    }
    result = source_collector_agent(state)

    assert result["query"] == "agritech"
    assert result["attempt_count"] == 2
