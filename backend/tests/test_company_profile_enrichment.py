from app.agents.company_profile_enrichment_agent import (
    company_profile_enrichment_agent,
)


def test_company_profile_enrichment_extracts_location_and_foundation():
    state = {
        "startups": [
            {
                "name": "DiagIA",
                "description": "Healthtech brasileira fundada em 2021 com sede em São Paulo, SP.",
                "sector": "healthtech",
                "possible_ai_signals": ["IA"],
                "sources": [
                    {
                        "title": "DiagIA capta rodada",
                        "url": "https://diagia.example.com/noticia",
                        "snippet": "A startup com sede em São Paulo, SP foi fundada em 2021.",
                    }
                ],
            }
        ],
        "errors": [],
    }

    result = company_profile_enrichment_agent(state)

    startup = result["startups"][0]
    assert startup["country"] == "Brazil"
    assert startup["state_region"] == "SP"
    assert startup["city"] == "São Paulo"
    assert startup["founded_year"] == 2021
    assert startup["website_url"] == "https://diagia.example.com"
    assert startup["company_profile"]["evidence"]


def test_company_profile_enrichment_keeps_unknown_values_as_none():
    state = {
        "startups": [
            {
                "name": "Startup Sem Perfil",
                "description": "Empresa usa IA para automação.",
                "sources": [
                    {
                        "title": "Startup Sem Perfil | Exame",
                        "url": "https://exame.com/startup-sem-perfil",
                        "snippet": "Empresa usa IA para automação.",
                    }
                ],
            }
        ],
        "errors": [],
    }

    result = company_profile_enrichment_agent(state)

    startup = result["startups"][0]
    assert startup["country"] is None
    assert startup["state_region"] is None
    assert startup["city"] is None
    assert startup["founded_year"] is None
    assert startup["website_url"] is None


def test_company_profile_enrichment_handles_empty_startups():
    state = {"startups": [], "errors": []}

    result = company_profile_enrichment_agent(state)

    assert result["errors"]
