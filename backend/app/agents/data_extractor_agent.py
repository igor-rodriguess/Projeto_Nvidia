import re
from typing import List, Dict, Any
from app.core.startup_analysis_state import StartupAnalysisState

# ---------------------------------------------------------------------------
# Keyword maps used for mock extraction.
# TODO: replace _extract_startup_from_source() with an LLM call (e.g. via
#       LangChain / NIM API) to do real named-entity + attribute extraction.
# ---------------------------------------------------------------------------

_SECTOR_KEYWORDS: Dict[str, List[str]] = {
    "healthtech": ["saúde", "health", "médico", "diagnóstico", "hospital", "clínica"],
    "fintech": ["fintech", "financeiro", "banco", "crédito", "pagamento", "finance"],
    "edtech": ["educação", "educacional", "edtech", "ensino", "aprendizado", "escola"],
    "agritech": ["agro", "agritech", "agrícola", "fazenda", "colheita", "irrigação"],
    "legaltech": ["jurídico", "legal", "legaltech", "advocacia", "contrato", "lei"],
    "retailtech": ["varejo", "retail", "e-commerce", "loja", "marketplace"],
}

_TECH_KEYWORDS: List[str] = [
    "inteligência artificial", "ia", "machine learning", "ml", "deep learning",
    "nlp", "visão computacional", "llm", "generativa", "automação", "robótica",
]


def _infer_sector(text: str) -> str:
    lower = text.lower()
    for sector, keywords in _SECTOR_KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            return sector
    return "tech"


def _infer_technologies(text: str) -> List[str]:
    lower = text.lower()
    return [kw for kw in _TECH_KEYWORDS if kw in lower] or ["ia"]


def _extract_name_from_title(title: str) -> str:
    """Derives a startup-like name from the source title (first segment before ' – ' or '|')."""
    for sep in (" – ", " | ", " - "):
        if sep in title:
            return title.split(sep)[0].strip()
    words = title.split()
    return " ".join(words[:4]) if len(words) >= 4 else title.strip()


def _extract_startup_from_source(source: Dict[str, Any], query: str) -> Dict[str, Any]:
    """
    Converts a single source dict into a structured startup dict.

    TODO: replace this function body with an LLM extraction call, e.g.:
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
        "technologies": _infer_technologies(full_text),
        "url": source.get("url", ""),
        "confidence": source.get("confidence", "low"),
        "source_title": title,
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
