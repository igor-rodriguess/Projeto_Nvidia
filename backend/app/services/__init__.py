from app.core.startup_analysis_state import StartupAnalysisState
from app.services.startup_search_pipeline import (
    StartupSearchPipeline,
    run_startup_discovery_pipeline,
)


async def run_pipeline(query: str) -> StartupAnalysisState:
    pipeline = StartupSearchPipeline()
    return await pipeline.run(query)


__all__ = ["StartupSearchPipeline", "run_pipeline", "run_startup_discovery_pipeline"]
