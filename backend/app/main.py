from fastapi import FastAPI

from app.routes import analysis_router, batch_router, health_router


app = FastAPI(
    title="NVIDIA Startup AI Radar API",
    description="API para investigacao em lote, analise de IA e briefing NVIDIA Inception.",
    version="1.0.0",
)
app.include_router(health_router)
app.include_router(batch_router)
app.include_router(analysis_router)
