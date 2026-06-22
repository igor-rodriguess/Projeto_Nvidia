from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services import run_pipeline


router = APIRouter(prefix="/startups", tags=["startups"])


class StartupSearchRequest(BaseModel):
    query: str = Field(..., min_length=1)


@router.post("/search")
async def search_startups(payload: StartupSearchRequest):
    return await run_pipeline(payload.query)
