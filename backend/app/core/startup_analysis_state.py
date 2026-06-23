from typing import Any, Dict, List, TypedDict


class StartupAnalysisState(TypedDict, total=False):
    query: str
    search_terms: List[str]
    sources: List[Dict[str, Any]]
    startups: List[Dict[str, Any]]
    validated_startups: List[Dict[str, Any]]
    nvidia_recommendations: List[Dict[str, Any]]
    attempt_count: int
    errors: List[str]
