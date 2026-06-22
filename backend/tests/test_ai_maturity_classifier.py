from app.agents.ai_maturity_classifier_agent import ai_maturity_classifier_agent
from app.core.startup_analysis_state import StartupAnalysisState


def test_ai_maturity_classifier_marks_advanced_startup():
    state: StartupAnalysisState = {
        "validated_startups": [
            {
                "name": "ModeloAI",
                "description": "Startup com LLM e machine learning.",
                "possible_ai_signals": ["IA", "LLM", "machine learning", "modelo"],
                "evidence_validation": {
                    "has_ai_evidence": True,
                    "confidence_level": "high",
                },
                "sources": [{"title": "ModeloAI", "url": "https://exame.com/modeloai"}],
            }
        ],
        "errors": [],
    }

    result = ai_maturity_classifier_agent(state)

    maturity = result["startups"][0]["ai_maturity"]
    assert maturity["level"] == "advanced"
    assert maturity["score"] >= 6
    assert maturity["method"] == "keyword_and_evidence_rules"


def test_ai_maturity_classifier_marks_unclear_when_no_ai_signal():
    state: StartupAnalysisState = {
        "validated_startups": [
            {
                "name": "Startup Sem Sinal",
                "description": "Empresa de serviços digitais.",
                "possible_ai_signals": [],
                "evidence_validation": {
                    "has_ai_evidence": False,
                    "confidence_level": "low",
                },
                "sources": [{"title": "Startup Sem Sinal", "url": "https://example.com"}],
            }
        ],
        "errors": [],
    }

    result = ai_maturity_classifier_agent(state)

    assert result["startups"][0]["ai_maturity"]["level"] == "unclear"


def test_ai_maturity_classifier_handles_empty_startups():
    state: StartupAnalysisState = {"validated_startups": [], "startups": [], "errors": []}

    result = ai_maturity_classifier_agent(state)

    assert result["startups"] == []
    assert result["errors"]
