from app.agents import source_collector_agent as collector_module
from app.services.startup_search_pipeline import run_startup_discovery_pipeline


def test_pipeline_complete_with_langgraph(monkeypatch):
    def fake_search(term: str, max_results: int):
        return [
            {
                "title": "NeuroSaúde - healthtech de IA",
                "href": "https://example.com/neurosaude",
                "body": "Startup brasileira usa inteligência artificial e dados para triagem médica.",
            }
        ]

    monkeypatch.setattr(collector_module, "_search_duckduckgo", fake_search)

    result = run_startup_discovery_pipeline("healthtech IA Brasil")

    assert result["query"] == "healthtech IA Brasil"
    assert result["search_terms"]
    assert result["sources"]
    assert result["startups"]
    assert result["errors"] == []


def test_pipeline_finishes_with_controlled_error_after_three_attempts(monkeypatch):
    monkeypatch.setattr(collector_module, "_search_duckduckgo", lambda term, max_results: [])

    result = run_startup_discovery_pipeline("consulta sem resultados")

    assert result["attempt_count"] == 3
    assert result["sources"] == []
    assert result["startups"] == []
    assert result["errors"]
