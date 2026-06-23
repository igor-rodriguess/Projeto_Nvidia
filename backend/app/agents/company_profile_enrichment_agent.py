import re
from typing import Any, Dict, List
from urllib.parse import urlparse

from app.core.startup_analysis_state import StartupAnalysisState


_BRAZIL_STATES = {
    "acre": "AC",
    "alagoas": "AL",
    "amapá": "AP",
    "amapa": "AP",
    "amazonas": "AM",
    "bahia": "BA",
    "ceará": "CE",
    "ceara": "CE",
    "distrito federal": "DF",
    "espírito santo": "ES",
    "espirito santo": "ES",
    "goiás": "GO",
    "goias": "GO",
    "maranhão": "MA",
    "maranhao": "MA",
    "mato grosso": "MT",
    "mato grosso do sul": "MS",
    "minas gerais": "MG",
    "pará": "PA",
    "paraíba": "PB",
    "paraiba": "PB",
    "paraná": "PR",
    "parana": "PR",
    "pernambuco": "PE",
    "piauí": "PI",
    "piaui": "PI",
    "rio de janeiro": "RJ",
    "rio grande do norte": "RN",
    "rio grande do sul": "RS",
    "rondônia": "RO",
    "rondonia": "RO",
    "roraima": "RR",
    "santa catarina": "SC",
    "são paulo": "SP",
    "sao paulo": "SP",
    "sergipe": "SE",
    "tocantins": "TO",
}
_BRAZIL_STATE_CODES = set(_BRAZIL_STATES.values())

_CITY_STATE_PATTERNS = [
    re.compile(
        r"\b(?:sediada|sediado|baseada|baseado|localizada|localizado|com sede)\s+em\s+([^,.;|]{2,60})[,/ -]+([A-Z]{2})\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b([A-Z][A-Za-z\s.-]{2,60})[,/ -]+([A-Z]{2})\b"
    ),
]

_FOUNDED_PATTERNS = [
    re.compile(r"\bfundad[ao]s?\s+em\s+(20\d{2}|19\d{2})\b", re.IGNORECASE),
    re.compile(r"\bcriad[ao]s?\s+em\s+(20\d{2}|19\d{2})\b", re.IGNORECASE),
    re.compile(r"\bdesde\s+(20\d{2}|19\d{2})\b", re.IGNORECASE),
]

_BRAZIL_TERMS = ("brasil", "brazil", "brasileira", "brasileiro")


def _startup_text(startup: Dict[str, Any]) -> str:
    source_text = " ".join(
        f"{source.get('title', '')} {source.get('snippet', '')}"
        for source in startup.get("sources", [])
    )
    return f"{startup.get('name', '')} {startup.get('description', '')} {source_text}"


def _extract_country(text: str) -> str | None:
    lower = text.lower()
    if any(term in lower for term in _BRAZIL_TERMS):
        return "Brazil"
    return None


def _extract_city_state(text: str) -> tuple[str | None, str | None]:
    for pattern in _CITY_STATE_PATTERNS:
        match = pattern.search(text)
        if not match:
            continue

        city = _clean_location(match.group(1))
        state = match.group(2).upper()
        if state in _BRAZIL_STATE_CODES:
            return city, state

    lower = text.lower()
    for state_name, state_code in _BRAZIL_STATES.items():
        if re.search(rf"\b{re.escape(state_name)}\b", lower):
            return None, state_code

    return None, None


def _clean_location(value: str) -> str:
    cleaned = re.sub(r"\s+", " ", value).strip(" .,-/")
    stop_words = ("startup", "empresa", "healthtech", "fintech", "edtech")
    words = cleaned.split()
    while words and words[0].lower() in stop_words:
        words.pop(0)
    return " ".join(words).strip() or cleaned


def _extract_founded_year(text: str) -> int | None:
    for pattern in _FOUNDED_PATTERNS:
        match = pattern.search(text)
        if match:
            return int(match.group(1))
    return None


def _extract_website_url(startup: Dict[str, Any]) -> str | None:
    for source in startup.get("sources", []):
        url = source.get("url", "")
        parsed = urlparse(url)
        if not parsed.netloc:
            continue

        domain = parsed.netloc.lower().replace("www.", "")
        if any(
            portal in domain
            for portal in (
                "exame.com",
                "startups.com.br",
                "startse.com",
                "linkedin.com",
                "youtube.com",
                "youtu.be",
            )
        ):
            continue

        return f"{parsed.scheme}://{parsed.netloc}"

    return None


def _profile_evidence(startup: Dict[str, Any]) -> List[Dict[str, str]]:
    evidence = []
    for source in startup.get("sources", []):
        if source.get("url"):
            evidence.append(
                {
                    "title": source.get("title", ""),
                    "url": source.get("url", ""),
                }
            )
    return evidence


def _enrich_startup(startup: Dict[str, Any]) -> Dict[str, Any]:
    text = _startup_text(startup)
    city, state_region = _extract_city_state(text)
    country = _extract_country(text) or ("Brazil" if state_region else None)
    founded_year = _extract_founded_year(text)
    website_url = _extract_website_url(startup)

    profile = {
        "country": country,
        "state_region": state_region,
        "city": city,
        "founded_year": founded_year,
        "website_url": website_url,
        "evidence": _profile_evidence(startup),
    }

    return {
        **startup,
        "country": country,
        "state_region": state_region,
        "city": city,
        "founded_year": founded_year,
        "website_url": website_url,
        "company_profile": profile,
    }


def company_profile_enrichment_agent(
    state: StartupAnalysisState,
) -> StartupAnalysisState:
    startups = state.get("startups", [])

    if not startups:
        state.setdefault("errors", []).append(
            "company_profile_enrichment_agent: no startups found in state"
        )
        return state

    state["startups"] = [_enrich_startup(startup) for startup in startups]
    return state
