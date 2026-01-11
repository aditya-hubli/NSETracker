"""Notification Service - FastAPI application with WebSocket support."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client

from shared.config import get_settings
from shared.logging_config import setup_logging
from .routes import router
from .websocket_manager import manager
from .alert_checker import AlertChecker
from .database import NotificationDatabase

# Setup logging
setup_logging()

# Global alert checker
alert_checker = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown."""
    global alert_checker
    
    # Startup
    print("Starting Notification Service...")
    
    # Initialize database
    settings = get_settings()
    db_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    db = NotificationDatabase(db_client)
    
    # Start alert checker
    alert_checker = AlertChecker(db)
    await alert_checker.start(check_interval=30)
    
    # Start price update broadcaster
    await manager.start_price_updates(interval_seconds=5)
    
    print("Notification Service started successfully")
    
    yield
    
    # Shutdown
    print("Shutting down Notification Service...")
    
    if alert_checker:
        await alert_checker.stop()
    
    await manager.stop_price_updates()
    
    print("Notification Service shut down")


# Create app
app = FastAPI(
    title="Notification Service",
    description="Real-time notifications, alerts, and WebSocket updates",
    version="1.0.0",
    lifespan=lifespan
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
        "service": "notification_service",
        "version": "1.0.0",
        "active_connections": len(manager.active_connections),
        "subscribed_symbols": len(manager.get_all_subscribed_symbols())
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
