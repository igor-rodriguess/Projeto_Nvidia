import re
import unicodedata
from difflib import SequenceMatcher
from typing import Any, Dict, List
from urllib.parse import urlparse

from app.core.startup_analysis_state import StartupAnalysisState


DESCRIPTION_SIMILARITY_THRESHOLD = 0.80

_NAME_SUFFIXES = {
    "ai",
    "app",
    "brasil",
    "digital",
    "health",
    "healthtech",
    "ia",
    "inteligencia artificial",
    "labs",
    "sa",
    "saude",
    "startup",
    "tech",
    "tecnologia",
}

_IGNORED_SOURCE_DOMAINS = {
    "blog.itau.com.br",
    "cubo.network",
    "exame.com",
    "itau.com.br",
    "linkedin.com",
    "pipelinevalor.globo.com",
    "revistapegn.globo.com",
    "startse.com",
    "startups.com.br",
    "valor.globo.com",
    "youtube.com",
    "youtu.be",
}


def _remove_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(char for char in normalized if not unicodedata.combining(char))


def _normalize_name(name: str) -> str:
    normalized = _remove_accents(name).lower()
    normalized = re.sub(r"[^a-z0-9\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    words = [word for word in normalized.split() if word not in _NAME_SUFFIXES]
    return " ".join(words) or normalized


def _source_domain(url: str) -> str | None:
    parsed = urlparse(url)
    if not parsed.netloc:
        return None
    return parsed.netloc.lower().replace("www.", "")


def _is_ignored_domain(domain: str) -> bool:
    return any(domain == ignored or domain.endswith(f".{ignored}") for ignored in _IGNORED_SOURCE_DOMAINS)


def _official_domain(startup: Dict[str, Any]) -> str | None:
    website_url = startup.get("website_url")
    if website_url:
        return _source_domain(website_url)

    for source in startup.get("sources", []):
        for field in ("final_url", "canonical_url", "url"):
            domain = _source_domain(source.get(field, "") or "")
            if domain and not _is_ignored_domain(domain):
                return domain

    return None


def _description_similarity(first: Dict[str, Any], second: Dict[str, Any]) -> float:
    first_description = _remove_accents(first.get("description", "")).lower().strip()
    second_description = _remove_accents(second.get("description", "")).lower().strip()
    if not first_description or not second_description:
        return 0.0
    return SequenceMatcher(None, first_description, second_description).ratio()


def _names_are_similar(first_name: str, second_name: str) -> bool:
    first = _normalize_name(first_name)
    second = _normalize_name(second_name)
    if not first or not second:
        return False
    if first == second:
        return True

    first_tokens = set(first.split())
    second_tokens = set(second.split())
    if first_tokens and second_tokens:
        smaller, bigger = sorted((first_tokens, second_tokens), key=len)
        if smaller.issubset(bigger):
            return True

    return SequenceMatcher(None, first, second).ratio() >= DESCRIPTION_SIMILARITY_THRESHOLD


def _same_company(first: Dict[str, Any], second: Dict[str, Any]) -> bool:
    if _names_are_similar(first.get("name", ""), second.get("name", "")):
        return True

    first_domain = _official_domain(first)
    second_domain = _official_domain(second)
    if first_domain and second_domain and first_domain == second_domain:
        return True

    return _description_similarity(first, second) >= DESCRIPTION_SIMILARITY_THRESHOLD


def _choose_primary_name(startups: List[Dict[str, Any]]) -> str:
    names = [startup.get("name", "").strip() for startup in startups if startup.get("name")]
    if not names:
        return "Unknown startup"
    return sorted(names, key=lambda name: (len(_normalize_name(name).split()), len(name)))[0]


def _merge_sources(startups: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    merged = []
    seen = set()

    for startup in startups:
        for source in startup.get("sources", []):
            key = source.get("url") or source.get("final_url") or source.get("title")
            if not key or key in seen:
                continue
            seen.add(key)
            merged.append(source)

    return merged


def _merge_urls(startups: List[Dict[str, Any]], sources: List[Dict[str, Any]]) -> List[str]:
    urls = []
    for startup in startups:
        if startup.get("website_url"):
            urls.append(startup["website_url"])
    for source in sources:
        urls.extend(
            url
            for url in (source.get("url"), source.get("final_url"), source.get("canonical_url"))
            if url
        )
    return list(dict.fromkeys(urls))


def _merge_ai_signals(startups: List[Dict[str, Any]]) -> List[str]:
    signals = []
    for startup in startups:
        signals.extend(startup.get("possible_ai_signals", []))
    return sorted(set(signal for signal in signals if signal))


def _choose_description(startups: List[Dict[str, Any]]) -> str:
    descriptions = [startup.get("description", "").strip() for startup in startups]
    descriptions = [description for description in descriptions if description]
    return max(descriptions, key=len) if descriptions else ""


def _merge_group(startups: List[Dict[str, Any]]) -> Dict[str, Any]:
    primary_name = _choose_primary_name(startups)
    sources = _merge_sources(startups)
    aliases = sorted(
        {
            startup.get("name", "").strip()
            for startup in startups
            if startup.get("name") and startup.get("name", "").strip() != primary_name
        }
    )

    base = startups[0].copy()
    base.update(
        {
            "name": primary_name,
            "aliases": aliases,
            "description": _choose_description(startups),
            "possible_ai_signals": _merge_ai_signals(startups),
            "sources": sources,
            "urls": _merge_urls(startups, sources),
            "merged_from_count": len(startups),
            "deduplication": {
                "normalized_name": _normalize_name(primary_name),
                "official_domain": _official_domain({"sources": sources, "website_url": base.get("website_url")}),
                "merged_names": [
                    startup.get("name", "").strip()
                    for startup in startups
                    if startup.get("name")
                ],
            },
        }
    )
    return base


def _deduplicate_startups(startups: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    groups: List[List[Dict[str, Any]]] = []

    for startup in startups:
        for group in groups:
            if any(_same_company(startup, grouped_startup) for grouped_startup in group):
                group.append(startup)
                break
        else:
            groups.append([startup])

    return [_merge_group(group) for group in groups]


def deduplication_agent(state: StartupAnalysisState) -> StartupAnalysisState:
    startups = state.get("startups", [])

    if not startups:
        state.setdefault("errors", []).append("deduplication_agent: no startups found in state")
        state["deduplicated_companies"] = []
        return state

    deduplicated = _deduplicate_startups(startups)
    state["deduplicated_companies"] = deduplicated
    state["startups"] = deduplicated
    return state
