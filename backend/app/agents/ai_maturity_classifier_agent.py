from typing import Any, Dict, List

from app.core.startup_analysis_state import StartupAnalysisState


_ADVANCED_TERMS = ["LLM", "modelo", "machine learning"]
_APPLIED_TERMS = ["inteligência artificial", "automação", "dados"]
_BASIC_TERMS = ["IA"]


def _normalize_signals(signals: List[str]) -> List[str]:
    return [signal.lower() for signal in signals]


def _maturity_score(startup: Dict[str, Any]) -> int:
    signals = _normalize_signals(startup.get("possible_ai_signals", []))
    validation = startup.get("evidence_validation", {})
    score = 0

    if any(term.lower() in signals for term in _BASIC_TERMS):
        score += 1
    if any(term.lower() in signals for term in _APPLIED_TERMS):
        score += 2
    if any(term.lower() in signals for term in _ADVANCED_TERMS):
        score += 3
    if validation.get("has_ai_evidence"):
        score += 1
    if validation.get("confidence_level") in {"medium", "high"}:
        score += 1

    return score


def _maturity_level(score: int) -> str:
    if score >= 6:
        return "advanced"
    if score >= 4:
        return "applied"
    if score >= 2:
        return "emerging"
    return "unclear"


def _classify_startup(startup: Dict[str, Any]) -> Dict[str, Any]:
    score = _maturity_score(startup)
    classification = {
        "level": _maturity_level(score),
        "score": score,
        "method": "keyword_and_evidence_rules",
    }

    return {**startup, "ai_maturity": classification}


def ai_maturity_classifier_agent(state: StartupAnalysisState) -> StartupAnalysisState:
    startups = state.get("validated_startups") or state.get("startups", [])

    if not startups:
        state.setdefault("errors", []).append(
            "ai_maturity_classifier_agent: no startups found in state"
        )
        state["startups"] = []
        return state

    state["startups"] = [_classify_startup(startup) for startup in startups]
    return state
