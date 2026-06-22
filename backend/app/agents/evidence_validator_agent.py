from typing import Any, Dict, List

from app.core.startup_analysis_state import StartupAnalysisState


_RELIABLE_DOMAINS = [
    "exame.com",
    "startups.com.br",
    "startse.com",
    "pipelinevalor.globo.com",
    "valor.globo.com",
    "sebrae.com.br",
    "endeavor.org.br",
    "braziljournal.com",
    "revistapegn.globo.com",
]

_AI_EVIDENCE_TERMS = [
    "IA",
    "inteligência artificial",
    "machine learning",
    "LLM",
    "automação",
    "dados",
    "modelo",
]


def _source_domain(url: str) -> str:
    clean_url = url.lower().replace("https://", "").replace("http://", "")
    return clean_url.split("/")[0].replace("www.", "")


def _is_reliable_source(url: str) -> bool:
    domain = _source_domain(url)
    return any(reliable_domain in domain for reliable_domain in _RELIABLE_DOMAINS)


def _count_reliable_sources(sources: List[Dict[str, Any]]) -> int:
    return sum(1 for source in sources if _is_reliable_source(source.get("url", "")))


def _confidence_level(source_count: int, reliable_source_count: int) -> str:
    if source_count >= 3 and reliable_source_count >= 1:
        return "high"
    if source_count >= 2 or reliable_source_count >= 1:
        return "medium"
    if source_count == 1:
        return "low"
    return "none"


def _has_ai_evidence(startup: Dict[str, Any]) -> bool:
    signals = startup.get("possible_ai_signals", [])
    if signals:
        return True

    text = f"{startup.get('name', '')} {startup.get('description', '')}".lower()
    return any(term.lower() in text for term in _AI_EVIDENCE_TERMS)


def _validate_startup(startup: Dict[str, Any]) -> Dict[str, Any]:
    sources = startup.get("sources", [])
    source_count = len(sources)
    reliable_source_count = _count_reliable_sources(sources)
    has_ai_evidence = _has_ai_evidence(startup)

    validation = {
        "is_publicly_supported": source_count > 0,
        "has_ai_evidence": has_ai_evidence,
        "source_count": source_count,
        "reliable_source_count": reliable_source_count,
        "confidence_level": _confidence_level(source_count, reliable_source_count),
    }

    return {**startup, "evidence_validation": validation}


def evidence_validator_agent(state: StartupAnalysisState) -> StartupAnalysisState:
    startups = state.get("startups", [])

    if not startups:
        state.setdefault("errors", []).append(
            "evidence_validator_agent: no startups found in state"
        )
        state["validated_startups"] = []
        return state

    validated_startups = [_validate_startup(startup) for startup in startups]
    state["validated_startups"] = validated_startups
    state["startups"] = validated_startups
    return state
