import re
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
    "cubo.network",
    "itau.com.br",
    "blog.itau.com.br",
]

_AI_EVIDENCE_TERMS = [
    "IA",
    "inteligencia artificial",
    "inteligência artificial",
    "machine learning",
    "LLM",
    "automacao",
    "automação",
    "dados",
    "modelo",
]


def _source_domain(url: str) -> str:
    clean_url = url.lower().replace("https://", "").replace("http://", "")
    return clean_url.split("/")[0].replace("www.", "")


def _source_text(source: Dict[str, Any]) -> str:
    return " ".join(
        str(source.get(field, "") or "")
        for field in (
            "title",
            "snippet",
            "page_title",
            "page_description",
            "page_text",
            "page_text_excerpt",
        )
    )


def _startup_evidence_text(startup: Dict[str, Any]) -> str:
    source_text = " ".join(_source_text(source) for source in startup.get("sources", []))
    return f"{startup.get('name', '')} {startup.get('description', '')} {source_text}"


def _is_reliable_source(url: str) -> bool:
    domain = _source_domain(url)
    return any(reliable_domain in domain for reliable_domain in _RELIABLE_DOMAINS)


def _count_reliable_sources(sources: List[Dict[str, Any]]) -> int:
    return sum(1 for source in sources if _is_reliable_source(source.get("url", "")))


def _count_scraped_sources(sources: List[Dict[str, Any]]) -> int:
    return sum(1 for source in sources if source.get("scrape_status") == "success")


def _has_ai_evidence(startup: Dict[str, Any]) -> bool:
    signals = startup.get("possible_ai_signals", [])
    if signals:
        return True

    text = _startup_evidence_text(startup).lower()
    return any(term.lower() in text for term in _AI_EVIDENCE_TERMS)


def _ai_evidence_terms(startup: Dict[str, Any]) -> List[str]:
    text = _startup_evidence_text(startup).lower()
    terms = set(startup.get("possible_ai_signals", []))

    for term in _AI_EVIDENCE_TERMS:
        normalized = term.lower()
        if normalized == "ia":
            if re.search(r"\bia\b", text):
                terms.add(term)
            continue

        if normalized in text:
            terms.add(term)

    return sorted(terms)


def _name_supported(startup: Dict[str, Any]) -> bool:
    name = (startup.get("name") or "").strip().lower()
    if len(name) < 3:
        return False

    for source in startup.get("sources", []):
        text = _source_text(source).lower()
        if name in text:
            return True

    return False


def _profile_supported(startup: Dict[str, Any]) -> Dict[str, bool]:
    text = _startup_evidence_text(startup).lower()
    return {
        "country": bool(startup.get("country") and startup["country"].lower() in text),
        "state_region": bool(
            startup.get("state_region")
            and re.search(rf"\b{re.escape(startup['state_region'].lower())}\b", text)
        ),
        "city": bool(startup.get("city") and startup["city"].lower() in text),
        "founded_year": bool(
            startup.get("founded_year")
            and str(startup["founded_year"]) in text
        ),
        "website_url": bool(startup.get("website_url")),
    }


def _quality_counts(sources: List[Dict[str, Any]]) -> Dict[str, int]:
    counts = {"high": 0, "medium": 0, "low": 0, "empty": 0, "unknown": 0}
    for source in sources:
        quality = source.get("extraction_quality") or "unknown"
        counts[quality if quality in counts else "unknown"] += 1
    return counts


def _verification_score(
    source_count: int,
    reliable_source_count: int,
    scraped_source_count: int,
    has_ai_evidence: bool,
    name_supported: bool,
    quality_counts: Dict[str, int],
) -> int:
    score = 0
    score += min(source_count, 3) * 10
    score += min(reliable_source_count, 2) * 15
    score += min(scraped_source_count, 2) * 10
    score += 20 if has_ai_evidence else 0
    score += 15 if name_supported else 0
    score += min(quality_counts.get("high", 0), 1) * 10
    score += min(quality_counts.get("medium", 0), 1) * 5
    return min(score, 100)


def _confidence_level(score: int) -> str:
    if score >= 80:
        return "high"
    if score >= 55:
        return "medium"
    if score >= 25:
        return "low"
    return "none"


def _verification_flags(
    startup: Dict[str, Any],
    has_ai_evidence: bool,
    name_supported: bool,
    scraped_source_count: int,
) -> List[str]:
    flags = []
    if not name_supported:
        flags.append("startup_name_not_confirmed_in_sources")
    if not has_ai_evidence:
        flags.append("ai_evidence_not_confirmed")
    if scraped_source_count == 0:
        flags.append("no_successfully_scraped_pages")
    if not startup.get("sources"):
        flags.append("no_public_sources")
    return flags


def _validate_startup(startup: Dict[str, Any]) -> Dict[str, Any]:
    sources = startup.get("sources", [])
    source_count = len(sources)
    reliable_source_count = _count_reliable_sources(sources)
    scraped_source_count = _count_scraped_sources(sources)
    has_ai_evidence = _has_ai_evidence(startup)
    name_supported = _name_supported(startup)
    quality_counts = _quality_counts(sources)
    score = _verification_score(
        source_count=source_count,
        reliable_source_count=reliable_source_count,
        scraped_source_count=scraped_source_count,
        has_ai_evidence=has_ai_evidence,
        name_supported=name_supported,
        quality_counts=quality_counts,
    )

    validation = {
        "is_publicly_supported": source_count > 0,
        "is_verified": score >= 70 and has_ai_evidence and name_supported,
        "has_ai_evidence": has_ai_evidence,
        "ai_evidence_terms": _ai_evidence_terms(startup),
        "name_supported_by_sources": name_supported,
        "profile_supported_by_sources": _profile_supported(startup),
        "source_count": source_count,
        "reliable_source_count": reliable_source_count,
        "scraped_source_count": scraped_source_count,
        "extraction_quality_counts": quality_counts,
        "verification_score": score,
        "confidence_level": _confidence_level(score),
        "verification_flags": _verification_flags(
            startup=startup,
            has_ai_evidence=has_ai_evidence,
            name_supported=name_supported,
            scraped_source_count=scraped_source_count,
        ),
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
