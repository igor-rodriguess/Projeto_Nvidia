from typing import Any

from app.core.startup_analysis_state import StartupAnalysisState


class DataExtractorAgent:
    """Converts unstructured collected text into structured startup data."""

    def run(self, state: StartupAnalysisState) -> dict[str, Any]:
        """
        Reads `raw_texts` and `collected_sources` from state.
        Returns `structured_data` with parsed startup records.
        """
        raise NotImplementedError
