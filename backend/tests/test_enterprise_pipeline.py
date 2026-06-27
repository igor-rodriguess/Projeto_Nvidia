from app.core.schemas import NVIDIARecommendationOutput
from app.services.enterprise_pipeline import run_enterprise_pipeline
from tests.test_scraper_agent import FakeSession


class FakeRecommender:
    def recommend(self, maturity):
        return NVIDIARecommendationOutput(
            startup=maturity.startup,
            recomendacoes=[],
            chunks_utilizados=[],
            aviso="Base de teste sem recomendações.",
        )


def test_enterprise_pipeline_returns_all_eight_trace_stages(monkeypatch, tmp_path):
    monkeypatch.setenv("SEARCH_PROVIDER", "searxng")
    monkeypatch.setenv("FIRECRAWL_API_KEY", "firecrawl-test")

    result = run_enterprise_pipeline(
        {
            "startup_name": "Clara Pagamentos",
            "site_oficial": "https://clara.com.br",
            "categoria": "Financeiro",
            "descricao_curta": "Plataforma financeira com automacao.",
        },
        session=FakeSession(),
        recommender=FakeRecommender(),
        cache=None,
        use_cache=False,
        delay_seconds=0,
        retry_wait_multiplier=0,
    )

    assert result["status"] in {"completo", "parcial"}
    assert set(result["trace"]) == {
        "search_planner",
        "scraper",
        "evidence_validator",
        "ai_maturity_classifier",
        "nvidia_recommender_rag",
        "recommendation_refiner",
        "impact_estimator",
        "briefing_generator",
    }
    assert result["classificacao"] in {"AI-native", "AI-enabled", "API-consumer", "Non-AI"}
    assert result["recomendacao"]["startup"] == "Clara Pagamentos"
    assert result["recomendacao_refinada"]["startup"] == "Clara Pagamentos"
    assert result["impacto_estimado"]["startup"] == "Clara Pagamentos"
    assert result["briefing_markdown"].startswith("# Briefing NVIDIA Inception")
    assert all("output" in stage for stage in result["trace"].values())
