"""API routes for notification service."""
import json
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, EmailStr

from supabase import create_client

from shared.config import get_settings
from .models import (
    PriceAlert,
    AlertStatus,
    AlertCreateRequest,
    Notification,
    SubscriptionRequest,
    WebSocketMessage,
)
from .database import NotificationDatabase
from .websocket_manager import manager
from .email_service import get_email_service

router = APIRouter(prefix="/notifications", tags=["notifications"])


def get_db():
    """Get database client."""
    settings = get_settings()
    client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    return NotificationDatabase(client)


# ==================== WebSocket Endpoints ====================

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for real-time updates.
    
    Events sent:
    - price_update: Real-time price updates for subscribed symbols
    - alert_triggered: When a price alert is triggered
    - notification: New notification
    
    Events received:
    - subscribe: Subscribe to stock symbols
    - unsubscribe: Unsubscribe from symbols
    """
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            event = message.get("event")
            payload = message.get("data", {})
            
            if event == "subscribe":
                symbols = payload.get("symbols", [])
                await manager.subscribe(user_id, symbols)
            
            elif event == "unsubscribe":
                symbols = payload.get("symbols", [])
                await manager.unsubscribe(user_id, symbols)
            
            elif event == "ping":
                await manager.send_personal_message(
                    user_id,
                    WebSocketMessage(event="pong", data={})
                )
    
    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        print(f"WebSocket error for {user_id}: {e}")
        manager.disconnect(user_id)


# ==================== Alert Endpoints ====================

@router.post("/alerts", response_model=PriceAlert)
async def create_alert(
    request: AlertCreateRequest,
    user_id: str = Query(..., description="User ID"),
    db: NotificationDatabase = Depends(get_db)
):
    """
    Create a new price alert.
    
    Alert conditions:
    - above: Trigger when price goes above target
    - below: Trigger when price falls below target
    - percent_up: Trigger when price increases by target %
    - percent_down: Trigger when price decreases by target %
    """
    # Get current price for reference
    import yfinance as yf
    ticker = yf.Ticker(request.symbol.upper())
    current_price = ticker.fast_info.last_price
    
    alert = PriceAlert(
        user_id=user_id,
        symbol=request.symbol.upper(),
        condition=request.condition,
        target_value=request.target_value,
        current_price=current_price,
        message=request.message,
        expires_at=(
            datetime.utcnow() + timedelta(days=request.expires_in_days)
            if request.expires_in_days else None
        )
    )
    
    return await db.create_alert(alert)


@router.get("/alerts", response_model=list[PriceAlert])
async def get_alerts(
    user_id: str = Query(..., description="User ID"),
    status: Optional[AlertStatus] = Query(None, description="Filter by status"),
    db: NotificationDatabase = Depends(get_db)
):
    """Get all alerts for a user."""
    return await db.get_user_alerts(user_id, status)


@router.delete("/alerts/{alert_id}")
async def cancel_alert(
    alert_id: str,
    user_id: str = Query(..., description="User ID"),
    db: NotificationDatabase = Depends(get_db)
):
    """Cancel an active alert."""
    success = await db.cancel_alert(alert_id, user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {"message": "Alert cancelled successfully"}


# ==================== Notification Endpoints ====================

@router.get("/", response_model=list[Notification])
async def get_notifications(
    user_id: str = Query(..., description="User ID"),
    unread_only: bool = Query(False, description="Only return unread notifications"),
    limit: int = Query(50, ge=1, le=100),
    db: NotificationDatabase = Depends(get_db)
):
    """Get notifications for a user."""
    return await db.get_user_notifications(user_id, unread_only, limit)


@router.get("/unread-count")
async def get_unread_count(
    user_id: str = Query(..., description="User ID"),
    db: NotificationDatabase = Depends(get_db)
):
    """Get count of unread notifications."""
    count = await db.get_unread_count(user_id)
    return {"unread_count": count}


@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    user_id: str = Query(..., description="User ID"),
    db: NotificationDatabase = Depends(get_db)
):
    """Mark a notification as read."""
    success = await db.mark_as_read(notification_id, user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"message": "Notification marked as read"}


@router.post("/read-all")
async def mark_all_read(
    user_id: str = Query(..., description="User ID"),
    db: NotificationDatabase = Depends(get_db)
):
    """Mark all notifications as read."""
    count = await db.mark_all_as_read(user_id)
    return {"message": f"Marked {count} notifications as read"}


# ==================== Email Notification Endpoints ====================

class EmailAlertRequest(BaseModel):
    """Request to send email alert."""
    email: EmailStr
    symbol: str
    condition: str
    target_price: float
    current_price: float
    change_percent: float = 0.0


class TestEmailRequest(BaseModel):
    """Request to send test email."""
    email: EmailStr


@router.post("/email/price-alert")
async def send_price_alert_email(request: EmailAlertRequest):
    """
    Send a price alert notification via email.
    
    This is called when a price alert is triggered to notify the user.
    """
    email_service = get_email_service()
    
    if not email_service.is_configured:
        raise HTTPException(
            status_code=503, 
            detail="Email service not configured. Set SMTP credentials in environment."
        )
    
    success = email_service.send_price_alert(
        to_email=request.email,
        symbol=request.symbol,
        condition=request.condition,
        target_price=request.target_price,
        current_price=request.current_price,
        change_percent=request.change_percent,
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send email")
    
    return {"message": "Price alert email sent successfully", "email": request.email}


@router.post("/email/test")
async def send_test_email(request: TestEmailRequest):
    """
    Send a test email to verify email configuration.
    """
    email_service = get_email_service()
    
    if not email_service.is_configured:
        return {
            "success": False,
            "message": "Email not configured. Add RESEND_API_KEY to your .env file (get one free at resend.com)",
            "required_vars": [
                "EMAIL_ENABLED=true",
                "RESEND_API_KEY=re_xxxxxxxxx",
            ]
        }
    
    success = email_service.send_test_email(request.email)
    
    if success:
        return {"success": True, "message": f"Test email sent to {request.email}"}
    else:
        return {"success": False, "message": "Failed to send test email. Check your API key."}


@router.get("/email/status")
async def get_email_status():
    """Check if email service is configured and ready."""
    email_service = get_email_service()
    settings = get_settings()
    
    return {
        "configured": email_service.is_configured,
        "smtp_host": settings.smtp_host,
        "smtp_port": settings.smtp_port,
        "from_email": settings.smtp_from_email or "(not set)",
        "enabled": settings.email_enabled,
    }

