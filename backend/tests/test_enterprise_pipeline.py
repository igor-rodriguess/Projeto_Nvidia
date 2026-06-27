from app.core.schemas import NVIDIARecommendationOutput
from app.services.enterprise_pipeline import EnterprisePipeline, run_enterprise_pipeline
from tests.test_scraper_agent import FakeSession


class FakeRecommender:
    def recommend(self, maturity):
        return NVIDIARecommendationOutput(
            startup=maturity.startup,
            recomendacoes=[],
            chunks_utilizados=[],
            aviso="Base de teste sem recomendações.",
        )


def test_enterprise_pipeline_returns_all_nine_trace_stages(monkeypatch, tmp_path):
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
        "inception_fit",
        "nvidia_recommender_rag",
        "recommendation_refiner",
        "impact_estimator",
        "briefing_generator",
    }
    assert result["classificacao"] in {"AI-native", "AI-enabled", "API-consumer", "Non-AI"}
    assert result["recomendacao"]["startup"] == "Clara Pagamentos"
    assert result["inception_fit"]["eligibility_status"] == "unknown"
    assert result["recomendacao_refinada"]["startup"] == "Clara Pagamentos"
    assert result["impacto_estimado"]["startup"] == "Clara Pagamentos"
    assert result["briefing_markdown"].startswith("# Briefing NVIDIA Inception")
    assert all("output" in stage for stage in result["trace"].values())


def test_source_warning_does_not_become_critical_when_results_exist():
    pipeline = object.__new__(EnterprisePipeline)
    state = {
        "warnings": [],
        "source_errors": [],
        "critical_errors": [],
        "errors": [],
    }
    output = {
        "status": "parcial",
        "resultados_buscas": [
            {"titulo": "Fonte", "url": "https://example.com", "snippet": "IA"}
        ],
        "paginas_completas": [],
        "erros": [{"erro": "Uma fonte retornou 403"}],
    }

    warnings, critical = pipeline._record_output_diagnostics(state, "scraper", output)

    assert warnings == ["scraper: Uma fonte retornou 403"]
    assert state["source_errors"] == warnings
    assert state["critical_errors"] == []
    assert critical is None


def test_missing_all_sources_is_a_critical_error():
    pipeline = object.__new__(EnterprisePipeline)
    state = {
        "warnings": [],
        "source_errors": [],
        "critical_errors": [],
        "errors": [],
    }

    _, critical = pipeline._record_output_diagnostics(
        state,
        "scraper",
        {"status": "parcial", "resultados_buscas": [], "paginas_completas": [], "erros": []},
    )

    assert critical == "scraper: nenhuma fonte utilizavel foi coletada"
    assert state["critical_errors"] == [critical]
