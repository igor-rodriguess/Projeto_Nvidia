from app.scraping import page_scraper as scraper_module
from app.scraping import source_collector as collector_module
from app.services import startup_search_pipeline
from app.services.startup_search_pipeline import run_startup_discovery_pipeline


def test_pipeline_complete_with_langgraph(monkeypatch):
    def fake_search(term: str, max_results: int):
        return [
            {
                "title": "NeuroSaude - healthtech de IA",
                "href": "https://example.com/neurosaude",
                "body": (
                    "Startup brasileira usa inteligencia artificial e dados "
                    "para triagem medica."
                ),
            }
        ]

    monkeypatch.setattr(collector_module, "_search_duckduckgo", fake_search)
    monkeypatch.setattr(
        scraper_module,
        "_fetch_page",
        lambda url: {
            "html": """
            <html>
              <head><title>NeuroSaude</title></head>
              <body><main>
                <p>Healthtech brasileira usa inteligencia artificial e dados para triagem medica.</p>
                <p>Empresa com sede em Sao Paulo, SP.</p>
              </main></body>
            </html>
            """,
            "http_status": 200,
            "final_url": url,
            "content_type": "text/html; charset=utf-8",
        },
    )
    monkeypatch.setattr(
        startup_search_pipeline,
        "persist_startup_discovery_result",
        lambda result: {"enabled": False, "saved": False},
    )

    result = run_startup_discovery_pipeline("healthtech IA Brasil")

    assert result["query"] == "healthtech IA Brasil"
    assert result["search_terms"]
    assert result["sources"]
    assert result["scrape_stats"]["scraped"] >= 1
    assert result["startups"]
    assert result["deduplicated_companies"]
    assert result["validated_startups"]
    assert "evidence_validation" in result["startups"][0]
    assert "ai_maturity" in result["startups"][0]
    assert result["nvidia_recommendations"]
    assert result["persistence"]["saved"] is False
    assert result["errors"] == []


def test_pipeline_finishes_with_controlled_error_after_three_attempts(monkeypatch):
    monkeypatch.setattr(collector_module, "_search_duckduckgo", lambda term, max_results: [])
    monkeypatch.setattr(
        startup_search_pipeline,
        "persist_startup_discovery_result",
        lambda result: {"enabled": False, "saved": False},
    )

    result = run_startup_discovery_pipeline("consulta sem resultados")

    assert result["attempt_count"] == 3
    assert result["sources"] == []
    assert result["startups"] == []
    assert result["validated_startups"] == []
    assert result["nvidia_recommendations"] == []
    assert result["errors"]
