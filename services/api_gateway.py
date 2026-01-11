"""API Gateway - Unified entry point for all services."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.order_service.routes import router as order_router
from services.payment_service.routes import router as payment_router
from services.stock_service.routes import router as stock_router
from services.user_service.routes import auth_router, router as user_router
from services.sentiment_service.routes import router as sentiment_router
from services.analytics_service.routes import router as analytics_router
from services.notification_service.routes import router as notification_router
from services.notification_service.websocket_manager import manager as ws_manager
from shared.config import get_settings
from shared.logging_config import setup_logging
from shared.cache import cache

settings = get_settings()
logger = setup_logging(
    service_name="api-gateway",
    level=settings.log_level,
    log_format=settings.log_format,
)

# Flag to track if Redpanda streaming is available
_streaming_enabled = False


async def _start_streaming() -> bool:
    """Start Redpanda streaming if available."""
    global _streaming_enabled
    
    try:
        from services.streaming_service import start_producer, start_consumer, get_consumer
        
        # Start producer (fetches prices, publishes to Redpanda)
        producer_started = await start_producer()
        if not producer_started:
            logger.warning("Failed to start streaming producer - Redpanda may not be running")
            return False
        
        # Start consumer with WebSocket broadcast handler
        async def broadcast_to_websockets(data: dict):
            """Broadcast price updates to subscribed WebSocket clients."""
            symbol = data.get("symbol")
            if symbol:
                from services.notification_service.models import WebSocketMessage
                message = WebSocketMessage(event="price_update", data=data)
                await ws_manager.broadcast_to_subscribers(symbol, message)
        
        consumer_started = await start_consumer()
        if consumer_started:
            consumer = get_consumer()
            if consumer:
                consumer.add_handler(broadcast_to_websockets)
        
        _streaming_enabled = True
        logger.info("Real-time streaming enabled via Redpanda")
        return True
        
    except Exception as e:
        logger.warning(f"Streaming not available: {e}")
        return False


async def _stop_streaming() -> None:
    """Stop Redpanda streaming."""
    global _streaming_enabled
    
    if _streaming_enabled:
        try:
            from services.streaming_service import stop_producer, stop_consumer
            await stop_consumer()
            await stop_producer()
            _streaming_enabled = False
            logger.info("Streaming stopped")
        except Exception as e:
            logger.error(f"Error stopping streaming: {e}")


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler."""
    logger.info("Starting API Gateway")
    
    # Initialize in-memory cache
    cache.connect()
    logger.info("In-memory cache initialized")
    
    # Try to start Redpanda streaming (graceful fallback if not available)
    streaming_ok = await _start_streaming()
    if not streaming_ok:
        # Fall back to direct yfinance polling via WebSocket manager
        logger.info("Falling back to direct price updates (no Redpanda)")
        await ws_manager.start_price_updates(interval_seconds=5)
    
    yield
    
    # Cleanup
    await _stop_streaming()
    await ws_manager.stop_price_updates()
    
    cache.disconnect()
    logger.info("Cache cleared")
    
    logger.info("Shutting down API Gateway")


app = FastAPI(
    title="Real-Time Stock Data Platform API",
    description="""
    Unified API Gateway for real-time stock data, analytics, and sentiment analysis.
    
    ## Features
    - **Users**: Authentication, registration, profile management
    - **Stocks**: Real-time prices, quotes, and market data
    - **Analytics**: Technical indicators, signals, screener
    - **Sentiment**: News and social media sentiment analysis
    - **Notifications**: Alerts, WebSocket updates, notifications
    - **Orders**: Trading order management
    - **Payments**: Payment processing
    """,
    version="1.0.0",
    lifespan=lifespan,
)

# CORS - allow dashboard to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all service routers
app.include_router(auth_router, prefix="/api/v1", tags=["authentication"])
app.include_router(user_router, prefix="/api/v1", tags=["users"])
app.include_router(stock_router, prefix="/api/v1", tags=["stocks"])
app.include_router(analytics_router, prefix="/api/v1", tags=["analytics"])
app.include_router(sentiment_router, prefix="/api/v1", tags=["sentiment"])
app.include_router(notification_router, prefix="/api/v1", tags=["notifications"])
app.include_router(order_router, prefix="/api/v1", tags=["orders"])
app.include_router(payment_router, prefix="/api/v1", tags=["payments"])


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "message": "Real-Time Stock Data Platform API",
        "docs": "/docs",
        "health": "/health",
        "version": "1.0.0",
    }


@app.get("/health")
async def health_check() -> dict[str, object]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "api-gateway",
        "streaming": "redpanda" if _streaming_enabled else "fallback",
        "websocket_connections": len(ws_manager.active_connections),
        "services": {
            "user": "active",
            "stock": "active",
            "analytics": "active",
            "sentiment": "active",
            "notification": "active",
            "order": "active",
            "payment": "active",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "services.api_gateway:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
