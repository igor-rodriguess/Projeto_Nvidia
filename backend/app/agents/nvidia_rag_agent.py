import os
import re
from typing import Any, Dict, List

from app.core.startup_analysis_state import StartupAnalysisState
from app.rag.knowledge_base import build_technology_documents, load_knowledge_base
from app.rag.retriever import retrieve_nvidia_context


MIN_RECOMMENDATION_SCORE = 4
MAX_RECOMMENDATIONS_PER_STARTUP = 4

_AI_SIGNAL_TERMS = {
    "ia",
    "inteligência artificial",
    "machine learning",
    "llm",
    "automação",
    "dados",
    "modelo",
    "generative ai",
    "inference",
    "agent",
    "copilot",
}

_DOMAIN_TECH_BOOSTS = {
    "healthtech": {"nvidia_clara": 4, "nvidia_inception": 1},
    "fintech": {"rapids_cudf_cuml": 2, "nvidia_ai_enterprise": 1},
    "edtech": {"nvidia_api_catalog": 1, "nvidia_nim": 1, "nemo_guardrails": 1},
    "agritech": {"nvidia_omniverse": 1, "rapids_cudf_cuml": 1, "nvidia_inception": 1},
    "legaltech": {"nemo_guardrails": 2, "nvidia_ai_enterprise": 1},
    "retailtech": {"rapids_cudf_cuml": 1, "nvidia_api_catalog": 1},
}


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


def _normalize(value: str) -> str:
    return value.lower().strip()


def _has_ai_evidence(startup: Dict[str, Any]) -> bool:
    if startup.get("possible_ai_signals"):
        return True

    validation = startup.get("evidence_validation", {})
    if validation.get("has_ai_evidence"):
        return True

    text_tokens = _tokenize(_startup_search_text(startup))
    return bool(text_tokens.intersection(_AI_SIGNAL_TERMS))


def _technology_index() -> Dict[str, Dict[str, Any]]:
    knowledge_base = load_knowledge_base()
    sources = knowledge_base["sources"]

    return {
        technology["id"]: {
            **technology,
            "sources": [
                {
                    "source_id": source_id,
                    "title": sources[source_id]["title"],
                    "url": sources[source_id]["url"],
                    "source_type": sources[source_id]["source_type"],
                }
                for source_id in technology["source_ids"]
            ],
        }
        for technology in knowledge_base["technologies"]
    }


def _document_index() -> Dict[str, Dict[str, Any]]:
    return {
        document["metadata"].get("technology_id", document["metadata"]["document_name"]): {
            "content": document["page_content"],
            "metadata": document["metadata"],
        }
        for document in build_technology_documents()
    }


def _fallback_retrieve_context(query: str, k: int = 8) -> List[Dict[str, Any]]:
    query_tokens = _tokenize(query)
    scored_contexts = []

    for context in _document_index().values():
        content_tokens = _tokenize(context["content"])
        score = len(query_tokens.intersection(content_tokens))
        if score == 0:
            continue

        scored_contexts.append((score, context))

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


def _candidate_technology_ids(query: str) -> set[str]:
    candidates = set()
    for context in _safe_retrieve_context(query):
        metadata = context.get("metadata", {})
        technology_id = metadata.get("technology_id")
        if metadata.get("knowledge_type") == "nvidia_technology" and technology_id:
            candidates.add(technology_id)

    return candidates


def _phrase_matches(text: str, phrases: List[str]) -> List[str]:
    lower = text.lower()
    return [phrase for phrase in phrases if phrase.lower() in lower]


def _score_technology(
    startup: Dict[str, Any],
    technology: Dict[str, Any],
    retrieved_candidate_ids: set[str],
) -> Dict[str, Any]:
    startup_text = _startup_search_text(startup)
    startup_tokens = _tokenize(startup_text)
    sector = _normalize(startup.get("sector", "tech"))
    maturity = _normalize(startup.get("ai_maturity", {}).get("level", "unclear"))
    technology_id = technology["id"]

    matched_startup_signals = _phrase_matches(startup_text, technology["startup_signals"])
    extracted_ai_signals = [
        signal for signal in startup.get("possible_ai_signals", []) if signal
    ]
    matched_ai_signals = sorted(
        set(extracted_ai_signals).union(startup_tokens.intersection(_AI_SIGNAL_TERMS))
    )

    score = 0
    score += len(matched_startup_signals) * 3

    if technology_id in retrieved_candidate_ids:
        score += 2

    if maturity in {_normalize(item) for item in technology["maturity_fit"]}:
        score += 1

    domain_boost = _DOMAIN_TECH_BOOSTS.get(sector, {}).get(technology_id, 0)
    score += domain_boost

    if technology_id == "nvidia_inception" and _has_ai_evidence(startup):
        score += 1

    if technology_id == "nvidia_api_catalog" and maturity in {"emerging", "applied"}:
        score += 1

    if not _has_ai_evidence(startup):
        score = 0

    return {
        "score": score,
        "matched_startup_signals": matched_startup_signals,
        "matched_ai_signals": matched_ai_signals,
        "matched_sector": sector if domain_boost else None,
        "retrieved_from_vector_store": technology_id in retrieved_candidate_ids,
    }


def _confidence(score: int) -> str:
    if score >= 8:
        return "high"
    if score >= 5:
        return "medium"
    return "low"


def _build_reason(
    startup: Dict[str, Any],
    technology: Dict[str, Any],
    evidence: Dict[str, Any],
) -> str:
    signals = evidence["matched_startup_signals"]
    sector = startup.get("sector", "tech")

    if signals:
        signal_text = ", ".join(signals[:3])
        return (
            f"{technology['name']} is relevant because the startup shows signals "
            f"aligned with {signal_text} in the '{sector}' context."
        )

    if evidence["matched_sector"]:
        return (
            f"{technology['name']} is relevant because the startup sector "
            f"'{sector}' maps to this NVIDIA domain in the curated RAG base."
        )

    return (
        f"{technology['name']} is relevant based on curated NVIDIA RAG evidence, "
        "but the match should be reviewed because explicit startup signals are limited."
    )


def _missing_evidence(startup: Dict[str, Any], technology: Dict[str, Any]) -> List[str]:
    gaps = []
    if not startup.get("possible_ai_signals"):
        gaps.append("No explicit AI signal was extracted from startup sources.")

    if "evidence_validation" not in startup:
        gaps.append("Public evidence was not validated before this RAG recommendation.")
    elif startup.get("evidence_validation", {}).get("confidence_level") in {"none", "low"}:
        gaps.append("Public evidence confidence is low.")

    if startup.get("ai_maturity", {}).get("level") in {None, "", "unclear"}:
        gaps.append("AI maturity is unclear.")

    if technology["id"] == "tensorrt_llm":
        gaps.append("Confirm whether the startup self-hosts LLMs before implementation.")

    return gaps


def _recommend_for_startup(startup: Dict[str, Any]) -> Dict[str, Any]:
    if not _has_ai_evidence(startup):
        return {
            "startup_name": startup.get("name", ""),
            "recommendations": [],
            "evidence_gap": (
                "Insufficient evidence to recommend NVIDIA technology because no "
                "explicit AI signal was found in the startup data."
            ),
        }

    query = _startup_search_text(startup)
    retrieved_candidate_ids = _candidate_technology_ids(query)
    technologies = _technology_index()
    scored = []

    for technology in technologies.values():
        evidence = _score_technology(startup, technology, retrieved_candidate_ids)
        if evidence["score"] < MIN_RECOMMENDATION_SCORE:
            continue

        scored.append((evidence["score"], technology, evidence))

    scored.sort(key=lambda item: item[0], reverse=True)
    recommendations = []

    for score, technology, evidence in scored[:MAX_RECOMMENDATIONS_PER_STARTUP]:
        recommendations.append(
            {
                "technology_id": technology["id"],
                "technology_name": technology["name"],
                "category": technology["category"],
                "confidence": _confidence(score),
                "match_score": score,
                "reason": _build_reason(startup, technology, evidence),
                "matched_startup_signals": evidence["matched_startup_signals"],
                "matched_ai_signals": evidence["matched_ai_signals"],
                "matched_sector": evidence["matched_sector"],
                "retrieved_from_vector_store": evidence["retrieved_from_vector_store"],
                "guardrails": technology["do_not_overclaim"],
                "missing_evidence": _missing_evidence(startup, technology),
                "sources": technology["sources"],
            }
        )

    evidence_gap = None
    if not recommendations:
        evidence_gap = (
            "AI evidence exists, but the curated RAG base did not find a strong "
            "enough NVIDIA technology match. Collect more product and infrastructure evidence."
        )

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
