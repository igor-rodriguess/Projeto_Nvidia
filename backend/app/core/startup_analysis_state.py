from typing import TypedDict, List, Dict, Any


class StartupAnalysisState(TypedDict):
    query: str
    search_terms: List[str]
    sources: List[Dict[str, Any]]
    startups: List[Dict[str, Any]]
    attempt_count: int
    errors: List[str]; 
