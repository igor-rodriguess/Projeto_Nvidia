from typing import List, Dict, Any
from app.core.startup_analysis_state import StartupAnalysisState

# ---------------------------------------------------------------------------
# Keyword maps for keyword-based extraction (mock layer).
# TODO: replace _extract_startup_from_source() with an LLM call via NIM API.
# ---------------------------------------------------------------------------

_SECTOR_KEYWORDS: Dict[str, List[str]] = {
    "healthtech": ["saúde", "health", "médico", "diagnóstico", "hospital", "clínica"],
    "fintech": ["fintech", "financeiro", "banco", "crédito", "pagamento", "finance"],
    "edtech": ["educação", "educacional", "edtech", "ensino", "aprendizado", "escola"],
    "agritech": ["agro", "agritech", "agrícola", "fazenda", "colheita", "irrigação"],
    "legaltech": ["jurídico", "legal", "legaltech", "advocacia", "contrato", "lei"],
    "retailtech": ["varejo", "retail", "e-commerce", "loja", "marketplace"],
}

_AI_SIGNAL_KEYWORDS: List[str] = [
    "ia",
    "inteligência artificial",
    "machine learning",
    "llm",
    "automação",
    "dados",
    "modelo",
    "deep learning",
    "nlp",
    "visão computacional",
    "generativa",
    "robótica",
]


def _infer_sector(text: str) -> str:
    lower = text.lower()
    for sector, keywords in _SECTOR_KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            return sector
    return "tech"


def _extract_ai_signals(text: str) -> List[str]:
    lower = text.lower()
    return [kw for kw in _AI_SIGNAL_KEYWORDS if kw in lower]


def _extract_name_from_title(title: str) -> str:
    for sep in (" – ", " | ", " - "):
        if sep in title:
            return title.split(sep)[0].strip()
    words = title.split()
    return " ".join(words[:4]) if len(words) >= 4 else title.strip()


def _extract_startup_from_source(source: Dict[str, Any], query: str) -> Dict[str, Any]:
    """
    Converts a single source dict into a structured startup dict.

    TODO: replace with an LLM extraction call:
        prompt = build_extraction_prompt(source, query)
        return llm_client.invoke(prompt)
    """
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
    """
    Converts unstructured collected sources into structured startup data.

    Reads:  state["sources"], state["query"]
    Writes: state["startups"]
    """
    sources: List[Dict[str, Any]] = state.get("sources", [])
    query: str = state.get("query", "")

    if not sources:
        state.setdefault("errors", []).append(
            "data_extractor_agent: no sources found in state"
        )
        state["startups"] = []
        return state

    state["startups"] = [_extract_startup_from_source(src, query) for src in sources]
    return state
