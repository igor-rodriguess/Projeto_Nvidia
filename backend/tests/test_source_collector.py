from app.scraping import source_collector as collector_module
from app.scraping.source_collector import source_collector_agent
from app.core.startup_analysis_state import StartupAnalysisState


def _fake_results(term: str, max_results: int):
    return [
        {
            "title": f"Startup Alpha - {term}",
            "href": "https://example.com/alpha",
            "body": "A Alpha usa inteligência artificial para dados em saúde.",
        },
        {
            "title": f"Startup Beta - {term}",
            "href": "https://example.com/beta",
            "body": "A Beta aplica machine learning no mercado financeiro.",
        },
    ][:max_results]


def test_source_collector_adds_real_search_shape_to_state(monkeypatch):
    monkeypatch.setattr(collector_module, "_search_duckduckgo", _fake_results)
    state: StartupAnalysisState = {
        "query": "startups brasileiras de saúde com IA",
        "search_terms": ["healthtech IA Brasil"],
        "errors": [],
    }

    result = source_collector_agent(state)

    assert len(result["sources"]) == 2


def test_source_collector_source_has_required_fields(monkeypatch):
    monkeypatch.setattr(collector_module, "_search_duckduckgo", _fake_results)
    state: StartupAnalysisState = {
        "query": "fintech IA",
        "search_terms": ["fintech IA Brasil"],
    }

    result = source_collector_agent(state)

    required_fields = {"title", "url", "snippet", "source_type", "collected_at"}
    for source in result["sources"]:
        assert required_fields.issubset(source.keys())


def test_source_collector_no_duplicate_urls(monkeypatch):
    monkeypatch.setattr(collector_module, "_search_duckduckgo", _fake_results)
    state: StartupAnalysisState = {
        "query": "edtech",
        "search_terms": ["edtech IA Brasil", "edtech IA Brasil startup"],
    }

    result = source_collector_agent(state)

    urls = [source["url"] for source in result["sources"]]
    assert len(urls) == len(set(urls))


def test_source_collector_empty_search_terms_returns_empty_sources():
    state: StartupAnalysisState = {
        "query": "qualquer coisa",
        "search_terms": [],
    }

    result = source_collector_agent(state)

    assert result["sources"] == []
    assert result["errors"]


def test_source_collector_handles_search_errors(monkeypatch):
    def failing_search(term: str, max_results: int):
        raise RuntimeError("search unavailable")

    monkeypatch.setattr(collector_module, "_search_duckduckgo", failing_search)
    state: StartupAnalysisState = {
        "query": "agritech",
        "search_terms": ["agritech IA"],
        "errors": [],
    }

    result = source_collector_agent(state)

    assert result["sources"] == []
    assert "search unavailable" in result["errors"][0]
