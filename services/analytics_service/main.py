"""Analytics Service - FastAPI application.

This service provides technical analysis, indicators, and stock screening.
It includes placeholder methods for ML model integration.

ML Integration:
- When ENABLE_ML_PREDICTIONS=true, the service will use trained models
- Models should be placed in ML_MODEL_PATH directory
- Supported models: LSTM price prediction, pattern recognition, anomaly detection
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.config import get_settings
from shared.logging_config import setup_logging
from .routes import router

# Setup logging
setup_logging()

# ML Configuration
ML_ENABLED = os.getenv("ENABLE_ML_PREDICTIONS", "false").lower() == "true"
ML_MODEL_PATH = os.getenv("ML_MODEL_PATH", "/app/models")

# Create app
app = FastAPI(
    title="Analytics Service",
    description="Technical analysis, indicators, and ML-powered stock predictions",
    version="1.0.0"
)

# CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "analytics_service",
        "version": "1.0.0",
        "ml_enabled": ML_ENABLED,
        "ml_model_path": ML_MODEL_PATH if ML_ENABLED else None
    }


@app.get("/config")
async def get_config():
    """Get service configuration."""
    return {
        "service": "analytics_service",
        "ml_predictions_enabled": ML_ENABLED,
        "ml_model_path": ML_MODEL_PATH,
        "available_models": _get_available_models() if ML_ENABLED else []
    }


def _get_available_models() -> list:
    """List available ML models in the model path."""
    if not os.path.exists(ML_MODEL_PATH):
        return []
    try:
        return [f for f in os.listdir(ML_MODEL_PATH) if os.path.isdir(os.path.join(ML_MODEL_PATH, f))]
    except Exception:
        return []


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
