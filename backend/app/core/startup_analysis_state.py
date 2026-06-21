from typing import Annotated, Any
from typing_extensions import TypedDict


class StartupAnalysisState(TypedDict):
    """Shared state passed between all agents in the pipeline."""

    # --- Input ---
    query: str

    # --- SearchPlannerAgent output ---
    search_terms: list[str]
    priority_sources: list[str]

    # --- SourceCollectorAgent output ---
    collected_sources: list[dict[str, Any]]
    raw_texts: list[str]

    # --- DataExtractorAgent output ---
    structured_data: list[dict[str, Any]]

    # --- EvidenceValidatorAgent output ---
    evidence: list[dict[str, Any]]

    # --- AIMaturityClassifierAgent output ---
    maturity_classification: str
    technical_gaps: list[str]

    # --- NVIDIARagAgent output ---
    nvidia_candidates: list[dict[str, Any]]

    # --- RecommendationAgent output ---
    recommendations: list[dict[str, Any]]

    # --- ImpactEstimatorAgent output ---
    impact_estimate: dict[str, Any]

    # --- BriefingGeneratorAgent output ---
    briefing: str
