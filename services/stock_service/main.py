"""Stock Service FastAPI Application."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.config import get_settings
from shared.logging_config import setup_logging

settings = get_settings()
logger = setup_logging(
    service_name="stock-service",
    level=settings.log_level,
    log_format=settings.log_format,
)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler."""
    logger.info("Starting Stock Service")
    yield
    logger.info("Shutting down Stock Service")


app = FastAPI(
    title="Stock Service",
    description="Real-time stock data and portfolio management",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from services.stock_service.routes import router  # noqa: E402

app.include_router(router, prefix="/api/v1")


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "stock-service"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "services.stock_service.main:app",
        host="0.0.0.0",
        port=8004,
        reload=True,
    )
