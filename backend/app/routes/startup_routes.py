from fastapi import APIRouter

from app.services import run_pipeline

router = APIRouter(prefix="/startups", tags=["startups"])


@router.post("/analyze")
async def analyze_startup(query: str):
    """Runs the full multiagent pipeline for a given query and returns the briefing."""
    result = await run_pipeline(query)
    return result
