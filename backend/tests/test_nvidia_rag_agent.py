from app.agents.nvidia_rag_agent import nvidia_rag_agent
from app.core.startup_analysis_state import StartupAnalysisState


def test_nvidia_rag_agent_recommends_with_sources_for_llm_startup():
    state: StartupAnalysisState = {
        "startups": [
            {
                "name": "ModeloAI",
                "description": "Startup que opera LLM self-hosted com agentes e problemas de inferência.",
                "sector": "tech",
                "possible_ai_signals": ["LLM", "modelo", "machine learning"],
                "ai_maturity": {"level": "advanced", "score": 7},
                "sources": [{"title": "Fonte", "url": "https://example.com"}],
            }
        ],
        "errors": [],
    }

    result = nvidia_rag_agent(state)

    recommendations = result["nvidia_recommendations"][0]["recommendations"]
    assert recommendations
    assert any(
        recommendation["technology_id"] in {"nvidia_nim", "tensorrt_llm"}
        for recommendation in recommendations
    )
    assert all(recommendation["sources"] for recommendation in recommendations)


def test_nvidia_rag_agent_reports_evidence_gap_without_ai_signals():
    state: StartupAnalysisState = {
        "startups": [
            {
                "name": "Padaria Digital",
                "description": "Sistema de gestão de pedidos para pequenos comércios.",
                "sector": "retailtech",
                "possible_ai_signals": [],
                "ai_maturity": {"level": "unclear", "score": 0},
                "sources": [{"title": "Fonte", "url": "https://example.com"}],
            }
        ],
        "errors": [],
    }

    result = nvidia_rag_agent(state)

    output = result["nvidia_recommendations"][0]
    assert output["recommendations"] == []
    assert "Insufficient evidence" in output["evidence_gap"]


def test_nvidia_rag_agent_handles_empty_startups():
    state: StartupAnalysisState = {"startups": [], "errors": []}

    result = nvidia_rag_agent(state)

    assert result["nvidia_recommendations"] == []
    assert result["errors"]
