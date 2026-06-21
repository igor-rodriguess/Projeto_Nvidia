from app.core.startup_analysis_state import StartupAnalysisState


class StartupSearchPipeline:
    """Orchestrates the full multiagent pipeline via LangGraph."""

    async def run(self, query: str) -> StartupAnalysisState:
        """
        Executes all agents in sequence and returns the final state
        containing the executive briefing and all intermediate results.
        """
        raise NotImplementedError
