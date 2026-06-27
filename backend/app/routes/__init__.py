from app.routes.analysis_routes import router as analysis_router
from app.routes.batch_routes import router as batch_router
from app.routes.health_routes import router as health_router
from app.routes.metrics_routes import router as metrics_router

__all__ = ["analysis_router", "batch_router", "health_router", "metrics_router"]
