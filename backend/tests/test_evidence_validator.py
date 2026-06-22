from app.agents.evidence_validator_agent import evidence_validator_agent
from app.core.startup_analysis_state import StartupAnalysisState


def test_evidence_validator_adds_validation_metadata():
    state: StartupAnalysisState = {
        "query": "healthtech IA",
        "startups": [
            {
                "name": "NeuroSaúde",
                "description": "Healthtech que usa inteligência artificial.",
                "sector": "healthtech",
                "possible_ai_signals": ["inteligência artificial"],
                "sources": [
                    {
                        "title": "NeuroSaúde capta investimento | Exame",
                        "url": "https://exame.com/negocios/neurosaude",
                    }
                ],
            }
        ],
        "errors": [],
    }

    result = evidence_validator_agent(state)

    validation = result["startups"][0]["evidence_validation"]
    assert validation["is_publicly_supported"] is True
    assert validation["has_ai_evidence"] is True
    assert validation["source_count"] == 1
    assert validation["reliable_source_count"] == 1
    assert validation["confidence_level"] == "medium"
    assert result["validated_startups"] == result["startups"]


def test_evidence_validator_handles_empty_startups():
    state: StartupAnalysisState = {"query": "sem startups", "startups": [], "errors": []}

    result = evidence_validator_agent(state)

    assert result["validated_startups"] == []
    assert result["errors"]
