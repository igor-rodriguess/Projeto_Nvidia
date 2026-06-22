import pytest

from app.agents.data_extractor_agent import data_extractor_agent
from app.core.startup_analysis_state import StartupAnalysisState

_SAMPLE_SOURCES = [
    {
        "title": "MedIA – startup de diagnóstico por IA | Exame",
        "url": "https://exame.com/negocios/media-startup",
        "snippet": "A MedIA utiliza inteligência artificial e machine learning para apoiar diagnósticos médicos.",
        "source_type": "public_search",
        "collected_at": "2026-06-22T00:00:00+00:00",
    },
    {
        "title": "CreditoIA – fintech de crédito inteligente",
        "url": "https://startse.com/creditoia",
        "snippet": "Startup fintech que usa IA e automação para análise de crédito.",
        "source_type": "public_search",
        "collected_at": "2026-06-22T00:00:00+00:00",
    },
]


def test_data_extractor_adds_startups_to_state():
    state: StartupAnalysisState = {
        "query": "startups brasileiras de saúde com IA",
        "sources": _SAMPLE_SOURCES,
    }
    result = data_extractor_agent(state)

    assert "startups" in result
    assert isinstance(result["startups"], list)
    assert len(result["startups"]) == len(_SAMPLE_SOURCES)


def test_data_extractor_startup_has_required_fields():
    state: StartupAnalysisState = {
        "query": "healthtech IA",
        "sources": _SAMPLE_SOURCES,
    }
    result = data_extractor_agent(state)

    required = {"name", "description", "sector", "possible_ai_signals", "sources"}
    for startup in result["startups"]:
        assert required.issubset(startup.keys()), (
            f"Startup está faltando campos: {required - startup.keys()}"
        )


def test_data_extractor_possible_ai_signals_is_list():
    state: StartupAnalysisState = {
        "query": "IA Brasil",
        "sources": [_SAMPLE_SOURCES[0]],
    }
    result = data_extractor_agent(state)

    signals = result["startups"][0]["possible_ai_signals"]
    assert isinstance(signals, list)
    assert len(signals) > 0


def test_data_extractor_sources_per_startup_has_title_and_url():
    state: StartupAnalysisState = {
        "query": "healthtech",
        "sources": [_SAMPLE_SOURCES[0]],
    }
    result = data_extractor_agent(state)

    startup_sources = result["startups"][0]["sources"]
    assert isinstance(startup_sources, list)
    assert all("title" in s and "url" in s for s in startup_sources)


def test_data_extractor_infers_healthtech_sector():
    state: StartupAnalysisState = {
        "query": "saúde digital",
        "sources": [_SAMPLE_SOURCES[0]],
    }
    result = data_extractor_agent(state)
    assert result["startups"][0]["sector"] == "healthtech"


def test_data_extractor_infers_fintech_sector():
    state: StartupAnalysisState = {
        "query": "fintech crédito",
        "sources": [_SAMPLE_SOURCES[1]],
    }
    result = data_extractor_agent(state)
    assert result["startups"][0]["sector"] == "fintech"


def test_data_extractor_empty_sources_returns_empty_startups():
    state: StartupAnalysisState = {
        "query": "qualquer coisa",
        "sources": [],
    }
    result = data_extractor_agent(state)
    assert result["startups"] == []
    assert len(result.get("errors", [])) > 0


def test_data_extractor_preserves_existing_state_fields():
    state: StartupAnalysisState = {
        "query": "agritech",
        "sources": [_SAMPLE_SOURCES[0]],
        "attempt_count": 3,
        "search_terms": ["agritech IA"],
    }
    result = data_extractor_agent(state)
    assert result["query"] == "agritech"
    assert result["attempt_count"] == 3
