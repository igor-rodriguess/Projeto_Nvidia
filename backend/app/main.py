from fastapi import FastAPI

from app.core.api_middleware import request_context_middleware
from app.routes import analysis_router, auth_router, batch_router, health_router, metrics_router


app = FastAPI(
    title="NVIDIA Startup AI Radar API",
    description="API para investigacao em lote, analise de IA e briefing NVIDIA Inception.",
    version="1.0.0",
)
app.middleware("http")(request_context_middleware)
app.include_router(health_router)
app.include_router(metrics_router)
app.include_router(auth_router)
app.include_router(batch_router)
app.include_router(analysis_router)
