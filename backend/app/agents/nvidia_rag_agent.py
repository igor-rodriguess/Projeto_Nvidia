import os
import re
from typing import Any, Dict, List

from app.core.startup_analysis_state import StartupAnalysisState
from app.rag.knowledge_base import build_technology_documents
from app.rag.retriever import retrieve_nvidia_context


MIN_RECOMMENDATION_SCORE = 2
MAX_RECOMMENDATIONS_PER_STARTUP = 4


def _tokenize(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-zA-Z0-9À-ÿ-]+", text.lower())
        if len(token) >= 3
    }


def _startup_search_text(startup: Dict[str, Any]) -> str:
    fields = [
        startup.get("name", ""),
        startup.get("description", ""),
        startup.get("sector", ""),
        " ".join(startup.get("possible_ai_signals", [])),
        startup.get("ai_maturity", {}).get("level", ""),
    ]
    return " ".join(fields)


def _fallback_retrieve_context(query: str, k: int = 8) -> List[Dict[str, Any]]:
    query_tokens = _tokenize(query)
    scored_contexts = []

    for document in build_technology_documents():
        content = document["page_content"]
        content_tokens = _tokenize(content)
        score = len(query_tokens.intersection(content_tokens))
        if score == 0:
            continue

        scored_contexts.append(
            (
                score,
                {
                    "content": content,
                    "metadata": document["metadata"],
                },
            )
        )

    scored_contexts.sort(key=lambda item: item[0], reverse=True)
    return [context for _, context in scored_contexts[:k]]


def _safe_retrieve_context(query: str) -> List[Dict[str, Any]]:
    if os.getenv("NVIDIA_RAG_USE_QDRANT", "false").lower() != "true":
        return _fallback_retrieve_context(query)

    try:
        contexts = retrieve_nvidia_context(query, k=8)
    except Exception:
        contexts = []

    return contexts or _fallback_retrieve_context(query)


def _context_score(startup: Dict[str, Any], context: Dict[str, Any]) -> int:
    startup_tokens = _tokenize(_startup_search_text(startup))
    context_tokens = _tokenize(context.get("content", ""))
    score = len(startup_tokens.intersection(context_tokens))

    maturity = startup.get("ai_maturity", {}).get("level")
    if maturity in context.get("content", "").lower():
        score += 1

    return score


def _confidence(score: int) -> str:
    if score >= 6:
        return "high"
    if score >= 3:
        return "medium"
    return "low"


def _evidence_gap(startup: Dict[str, Any], score: int) -> str | None:
    if score >= MIN_RECOMMENDATION_SCORE:
        return None

    return (
        f"Insufficient evidence to recommend NVIDIA technology for "
        f"{startup.get('name', 'startup')} from the available startup signals."
    )


def _build_reason(startup: Dict[str, Any], context: Dict[str, Any]) -> str:
    metadata = context.get("metadata", {})
    technology_name = metadata.get("technology_name", metadata.get("document_name"))
    signals = startup.get("possible_ai_signals", [])
    sector = startup.get("sector", "tech")

    signal_text = ", ".join(signals) if signals else "limited explicit AI signals"
    return (
        f"{technology_name} matches the startup sector '{sector}' and signals "
        f"({signal_text}) based on curated NVIDIA RAG evidence."
    )


def _recommend_for_startup(startup: Dict[str, Any]) -> Dict[str, Any]:
    query = _startup_search_text(startup)
    contexts = _safe_retrieve_context(query)
    scored_contexts = []

    for context in contexts:
        metadata = context.get("metadata", {})
        if metadata.get("knowledge_type") != "nvidia_technology":
            continue

        score = _context_score(startup, context)
        if score < MIN_RECOMMENDATION_SCORE:
            continue

        scored_contexts.append((score, context))

    scored_contexts.sort(key=lambda item: item[0], reverse=True)
    recommendations = []
    seen_technologies = set()

    for score, context in scored_contexts:
        metadata = context["metadata"]
        technology_id = metadata.get("technology_id")
        if technology_id in seen_technologies:
            continue

        seen_technologies.add(technology_id)
        recommendations.append(
            {
                "technology_id": technology_id,
                "technology_name": metadata.get("technology_name"),
                "category": metadata.get("category"),
                "confidence": _confidence(score),
                "match_score": score,
                "reason": _build_reason(startup, context),
                "sources": metadata.get("sources", []),
            }
        )

        if len(recommendations) >= MAX_RECOMMENDATIONS_PER_STARTUP:
            break

    evidence_gap = None
    if not recommendations:
        evidence_gap = _evidence_gap(startup, 0)

    return {
        "startup_name": startup.get("name", ""),
        "recommendations": recommendations,
        "evidence_gap": evidence_gap,
    }


def nvidia_rag_agent(state: StartupAnalysisState) -> StartupAnalysisState:
    startups = state.get("startups", [])

    if not startups:
        state.setdefault("errors", []).append("nvidia_rag_agent: no startups found")
        state["nvidia_recommendations"] = []
        return state

    state["nvidia_recommendations"] = [
        _recommend_for_startup(startup) for startup in startups
    ]
    return state
