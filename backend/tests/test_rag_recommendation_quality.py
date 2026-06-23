from app.agents.nvidia_rag_agent import nvidia_rag_agent


def _recommend(startup):
    state = {"startups": [startup], "errors": []}
    result = nvidia_rag_agent(state)
    return result["nvidia_recommendations"][0]["recommendations"]


def _startup(
    description,
    sector="tech",
    signals=None,
    maturity="applied",
    evidence_confidence="medium",
):
    return {
        "name": "Startup Teste",
        "description": description,
        "sector": sector,
        "possible_ai_signals": signals or ["IA"],
        "ai_maturity": {"level": maturity, "score": 4},
        "evidence_validation": {"confidence_level": evidence_confidence},
        "sources": [{"title": "Fonte", "url": "https://example.com"}],
    }


def test_healthcare_scenario_prioritizes_clara():
    recommendations = _recommend(
        _startup(
            "Healthtech usa IA em diagnóstico e fluxos clínicos hospitalares.",
            sector="healthtech",
            signals=["IA"],
            maturity="emerging",
        )
    )

    assert recommendations[0]["technology_id"] == "nvidia_clara"


def test_speech_scenario_recommends_riva():
    recommendations = _recommend(
        _startup(
            "Produto usa speech-to-text e text-to-speech em voice assistant para call center.",
            signals=["IA", "automação"],
        )
    )

    assert any(item["technology_id"] == "nvidia_riva" for item in recommendations)


def test_robotics_scenario_recommends_isaac():
    recommendations = _recommend(
        _startup(
            "Startup cria robot simulation, percepção e autonomia para AMRs industriais.",
            signals=["IA", "machine learning"],
            maturity="advanced",
        )
    )

    assert any(item["technology_id"] == "nvidia_isaac" for item in recommendations)


def test_cybersecurity_scenario_recommends_morpheus():
    recommendations = _recommend(
        _startup(
            "Plataforma de cybersecurity analisa logs para anomaly detection e threat detection em SOC.",
            signals=["IA", "dados"],
            maturity="advanced",
        )
    )

    assert any(item["technology_id"] == "nvidia_morpheus" for item in recommendations)


def test_self_hosted_llm_scenario_recommends_tensorrt_llm_and_nim():
    recommendations = _recommend(
        _startup(
            "Startup opera self-hosted LLM com GPU inference, latency e cost per token como gargalos.",
            signals=["LLM", "modelo", "machine learning"],
            maturity="advanced",
        )
    )
    ids = {item["technology_id"] for item in recommendations}

    assert "tensorrt_llm" in ids
    assert "nvidia_nim" in ids


def test_non_ai_scenario_returns_no_recommendation():
    state = {
        "startups": [
            {
                "name": "Agenda Local",
                "description": "Sistema simples de agendamento para salões de beleza.",
                "sector": "retailtech",
                "possible_ai_signals": [],
                "ai_maturity": {"level": "unclear", "score": 0},
                "evidence_validation": {
                    "has_ai_evidence": False,
                    "confidence_level": "medium",
                },
                "sources": [{"title": "Fonte", "url": "https://example.com"}],
            }
        ],
        "errors": [],
    }

    result = nvidia_rag_agent(state)
    output = result["nvidia_recommendations"][0]

    assert output["recommendations"] == []
    assert output["evidence_gap"]
