from fastapi import FastAPI

from app.routes.startup_routes import router as startup_router

app = FastAPI(
    title="NVIDIA Startup AI Radar",
    description="Multiagent platform for identifying and analyzing Brazilian AI-native startups.",
    version="0.1.0",
)

app.include_router(startup_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
