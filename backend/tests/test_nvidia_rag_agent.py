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
    assert all(recommendation["guardrails"] for recommendation in recommendations)
    assert all("missing_evidence" in recommendation for recommendation in recommendations)


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


def test_nvidia_rag_agent_prioritizes_healthcare_domain_for_healthtech():
    state: StartupAnalysisState = {
        "startups": [
            {
                "name": "DiagIA",
                "description": "Healthtech que usa IA para apoiar diagnóstico em hospitais.",
                "sector": "healthtech",
                "possible_ai_signals": ["IA"],
                "ai_maturity": {"level": "emerging", "score": 2},
                "evidence_validation": {"confidence_level": "medium"},
                "sources": [{"title": "Fonte", "url": "https://example.com"}],
            }
        ],
        "errors": [],
    }

    result = nvidia_rag_agent(state)

    recommendations = result["nvidia_recommendations"][0]["recommendations"]
    assert recommendations[0]["technology_id"] == "nvidia_clara"
    assert recommendations[0]["matched_sector"] == "healthtech"
    assert "IA" in recommendations[0]["matched_ai_signals"]


def test_nvidia_rag_agent_does_not_recommend_low_signal_data_tools_for_generic_ai():
    state: StartupAnalysisState = {
        "startups": [
            {
                "name": "Chat Escola",
                "description": "Edtech com chatbot de IA para responder dúvidas de alunos.",
                "sector": "edtech",
                "possible_ai_signals": ["IA", "automação"],
                "ai_maturity": {"level": "emerging", "score": 2},
                "sources": [{"title": "Fonte", "url": "https://example.com"}],
            }
        ],
        "errors": [],
    }

    result = nvidia_rag_agent(state)

    technology_ids = {
        recommendation["technology_id"]
        for recommendation in result["nvidia_recommendations"][0]["recommendations"]
    }
    assert "rapids_cudf_cuml" not in technology_ids


def test_nvidia_rag_agent_marks_missing_validation_evidence():
    state: StartupAnalysisState = {
        "startups": [
            {
                "name": "ModeloAI",
                "description": "Startup que opera LLM self-hosted.",
                "sector": "tech",
                "possible_ai_signals": ["LLM"],
                "ai_maturity": {"level": "advanced", "score": 7},
                "sources": [{"title": "Fonte", "url": "https://example.com"}],
            }
        ],
        "errors": [],
    }

    result = nvidia_rag_agent(state)

    missing_evidence = result["nvidia_recommendations"][0]["recommendations"][0][
        "missing_evidence"
    ]
    assert "Public evidence was not validated before this RAG recommendation." in missing_evidence
