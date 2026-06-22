import re
from typing import Any, Dict, List

from app.core.startup_analysis_state import StartupAnalysisState


_SECTOR_KEYWORDS: Dict[str, List[str]] = {
    "healthtech": ["saúde", "health", "médico", "diagnóstico", "hospital", "clínica"],
    "fintech": ["fintech", "financeiro", "banco", "crédito", "pagamento", "finance"],
    "edtech": ["educação", "educacional", "edtech", "ensino", "aprendizado", "escola"],
    "agritech": ["agro", "agritech", "agrícola", "fazenda", "colheita", "irrigação"],
    "legaltech": ["jurídico", "legal", "legaltech", "advocacia", "contrato", "lei"],
    "retailtech": ["varejo", "retail", "e-commerce", "loja", "marketplace"],
}

_AI_SIGNAL_KEYWORDS: List[str] = [
    "IA",
    "inteligência artificial",
    "machine learning",
    "LLM",
    "automação",
    "dados",
    "modelo",
]


def _infer_sector(text: str) -> str:
    lower = text.lower()
    for sector, keywords in _SECTOR_KEYWORDS.items():
        if any(keyword in lower for keyword in keywords):
            return sector
    return "tech"


def _extract_ai_signals(text: str) -> List[str]:
    lower = text.lower()
    signals = []

    for keyword in _AI_SIGNAL_KEYWORDS:
        normalized = keyword.lower()
        if normalized == "ia":
            if re.search(r"\bia\b", lower):
                signals.append(keyword)
            continue

        if normalized in lower:
            signals.append(keyword)

    return signals


def _extract_name_from_title(title: str) -> str:
    for separator in (" – ", " | ", " - ", ":"):
        if separator in title:
            return title.split(separator)[0].strip()

    words = title.split()
    return " ".join(words[:4]) if len(words) >= 4 else title.strip()


def _extract_startup_from_source(source: Dict[str, Any], query: str) -> Dict[str, Any]:
    title = source.get("title", "")
    snippet = source.get("snippet", "")
    full_text = f"{title} {snippet} {query}"

    return {
        "name": _extract_name_from_title(title),
        "description": snippet or title,
        "sector": _infer_sector(full_text),
        "possible_ai_signals": _extract_ai_signals(full_text),
        "sources": [{"title": title, "url": source.get("url", "")}],
    }


def data_extractor_agent(state: StartupAnalysisState) -> StartupAnalysisState:
    sources: List[Dict[str, Any]] = state.get("sources", [])
    query: str = state.get("query", "")

    if not sources:
        state.setdefault("errors", []).append(
            "data_extractor_agent: no sources found in state"
        )
        state["startups"] = []
        return state

    state["startups"] = [
        _extract_startup_from_source(source, query) for source in sources
    ]
    return state
