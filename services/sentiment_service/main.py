"""Sentiment Service - FastAPI application.

This service provides real-time market sentiment analysis from news and social media.
It includes placeholder methods for ML-based sentiment analysis.

ML Integration:
- When ENABLE_ML_SENTIMENT=true, the service will use FinBERT or custom models
- Models should be placed in ML_MODEL_PATH directory
- Supported models: FinBERT, custom fine-tuned transformers
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
ML_ENABLED = os.getenv("ENABLE_ML_SENTIMENT", "false").lower() == "true"
ML_MODEL_PATH = os.getenv("ML_MODEL_PATH", "/app/models")

# Create app
app = FastAPI(
    title="Sentiment Service",
    description="Real-time market sentiment analysis with ML-powered NLP",
    version="1.0.0"
)

# CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
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
        "service": "sentiment_service",
        "version": "1.0.0",
        "ml_enabled": ML_ENABLED,
        "ml_model_path": ML_MODEL_PATH if ML_ENABLED else None
    }


@app.get("/config")
async def get_config():
    """Get service configuration."""
    return {
        "service": "sentiment_service",
        "ml_sentiment_enabled": ML_ENABLED,
        "ml_model_path": ML_MODEL_PATH,
        "available_models": _get_available_models() if ML_ENABLED else [],
        "supported_sources": ["news", "yfinance", "google_news"]
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
    uvicorn.run(app, host="0.0.0.0", port=8003)
