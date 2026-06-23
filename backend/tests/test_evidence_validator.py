from app.agents.evidence_validator_agent import evidence_validator_agent
from app.core.startup_analysis_state import StartupAnalysisState


def test_evidence_validator_adds_validation_metadata():
    state: StartupAnalysisState = {
        "query": "healthtech IA",
        "startups": [
            {
                "name": "NeuroSaude",
                "description": "Healthtech que usa inteligencia artificial.",
                "sector": "healthtech",
                "possible_ai_signals": ["inteligencia artificial"],
                "sources": [
                    {
                        "title": "NeuroSaude capta investimento | Exame",
                        "url": "https://exame.com/negocios/neurosaude",
                        "snippet": "NeuroSaude usa inteligencia artificial em saude.",
                        "page_text": (
                            "NeuroSaude e uma healthtech brasileira que usa "
                            "inteligencia artificial para apoiar diagnosticos."
                        ),
                        "scrape_status": "success",
                        "extraction_quality": "high",
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
    assert validation["scraped_source_count"] == 1
    assert validation["name_supported_by_sources"] is True
    assert validation["is_verified"] is True
    assert validation["verification_score"] >= 70
    assert validation["confidence_level"] == "high"
    assert validation["verification_flags"] == []
    assert result["validated_startups"] == result["startups"]


def test_evidence_validator_flags_weak_or_unconfirmed_evidence():
    state: StartupAnalysisState = {
        "query": "startup IA",
        "startups": [
            {
                "name": "Empresa X",
                "description": "Resultado generico sem confirmacao.",
                "sector": "tech",
                "possible_ai_signals": [],
                "sources": [
                    {
                        "title": "Lista de empresas",
                        "url": "https://example.com/lista",
                        "snippet": "Resultado agregado sem detalhes.",
                        "scrape_status": "failed",
                        "scrape_error": "timeout",
                        "extraction_quality": "unknown",
                    }
                ],
            }
        ],
        "errors": [],
    }

    result = evidence_validator_agent(state)

    validation = result["startups"][0]["evidence_validation"]
    assert validation["is_verified"] is False
    assert validation["has_ai_evidence"] is False
    assert validation["name_supported_by_sources"] is False
    assert validation["scraped_source_count"] == 0
    assert "startup_name_not_confirmed_in_sources" in validation["verification_flags"]
    assert "ai_evidence_not_confirmed" in validation["verification_flags"]
    assert "no_successfully_scraped_pages" in validation["verification_flags"]


def test_evidence_validator_handles_empty_startups():
    state: StartupAnalysisState = {"query": "sem startups", "startups": [], "errors": []}

    result = evidence_validator_agent(state)

    assert result["validated_startups"] == []
    assert result["errors"]
