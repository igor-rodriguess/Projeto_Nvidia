from app.core.startup_analysis_state import StartupAnalysisState
from app.services.startup_search_pipeline import StartupSearchPipeline


async def run_pipeline(query: str) -> StartupAnalysisState:
    pipeline = StartupSearchPipeline()
    return await pipeline.run(query)
