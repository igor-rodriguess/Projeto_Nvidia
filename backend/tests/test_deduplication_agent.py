from app.agents.deduplication_agent import deduplication_agent
from app.core.startup_analysis_state import StartupAnalysisState


def _startup(name, description="Empresa de IA.", url="https://example.com", signals=None):
    return {
        "name": name,
        "description": description,
        "sector": "tech",
        "possible_ai_signals": signals or ["IA"],
        "sources": [
            {
                "title": name,
                "url": url,
                "snippet": description,
            }
        ],
    }


def test_deduplicates_exact_same_name():
    state: StartupAnalysisState = {
        "startups": [
            _startup("Alice", url="https://news.example/a"),
            _startup("Alice", url="https://blog.example/a"),
        ],
        "errors": [],
    }

    result = deduplication_agent(state)

    assert len(result["startups"]) == 1
    assert result["startups"][0]["merged_from_count"] == 2


def test_deduplicates_similar_names():
    state: StartupAnalysisState = {
        "startups": [
            _startup("Alice", url="https://alice.com.br"),
            _startup("Alice Saude", url="https://alice.com.br/sobre"),
        ],
        "errors": [],
    }

    result = deduplication_agent(state)

    assert len(result["startups"]) == 1
    assert result["startups"][0]["name"] == "Alice"
    assert result["startups"][0]["aliases"] == ["Alice Saude"]


def test_deduplicates_same_domain():
    state: StartupAnalysisState = {
        "startups": [
            _startup("Empresa Alpha", url="https://www.alpha.com.br"),
            _startup("Alpha AI", url="https://alpha.com.br/cases"),
        ],
        "errors": [],
    }

    result = deduplication_agent(state)

    assert len(result["startups"]) == 1


def test_deduplicates_same_official_website():
    first = _startup("Beta", url="https://noticia.example/beta")
    second = _startup("Beta Tecnologia", url="https://outra.example/beta")
    first["website_url"] = "https://beta.ai"
    second["website_url"] = "https://www.beta.ai/"

    result = deduplication_agent({"startups": [first, second], "errors": []})

    assert len(result["startups"]) == 1
    assert result["startups"][0]["merged_from_count"] == 2


def test_keeps_different_companies_separated():
    state: StartupAnalysisState = {
        "startups": [
            _startup("Alice", description="Healthtech com IA.", url="https://alice.com.br"),
            _startup("Brisa", description="Fintech de credito.", url="https://brisa.com.br"),
        ],
        "errors": [],
    }

    result = deduplication_agent(state)

    assert len(result["startups"]) == 2


def test_consolidates_sources_aliases_and_ai_signals():
    state: StartupAnalysisState = {
        "startups": [
            _startup("Clara", url="https://clara.ai", signals=["IA", "dados"]),
            _startup("Clara Health", url="https://clara.ai/blog", signals=["machine learning"]),
        ],
        "errors": [],
    }

    result = deduplication_agent(state)
    company = result["startups"][0]

    assert len(company["sources"]) == 2
    assert company["aliases"] == ["Clara Health"]
    assert company["possible_ai_signals"] == ["IA", "dados", "machine learning"]
    assert company["deduplication"]["merged_names"] == ["Clara", "Clara Health"]
    assert result["deduplicated_companies"] == result["startups"]
