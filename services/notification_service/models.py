"""Data models for notification service."""
from datetime import datetime
from enum import Enum
from typing import Optional, Any

from pydantic import BaseModel, Field


class NotificationType(str, Enum):
    """Type of notification."""
    PRICE_ALERT = "price_alert"
    PRICE_CHANGE = "price_change"
    VOLUME_SPIKE = "volume_spike"
    SENTIMENT_SHIFT = "sentiment_shift"
    SIGNAL_CHANGE = "signal_change"
    NEWS_ALERT = "news_alert"
    WATCHLIST_UPDATE = "watchlist_update"
    SYSTEM = "system"


class AlertCondition(str, Enum):
    """Condition for price alerts."""
    ABOVE = "above"
    BELOW = "below"
    PERCENT_UP = "percent_up"
    PERCENT_DOWN = "percent_down"


class AlertStatus(str, Enum):
    """Status of an alert."""
    ACTIVE = "active"
    TRIGGERED = "triggered"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class PriceAlert(BaseModel):
    """User-defined price alert."""
    id: Optional[str] = None
    user_id: str
    symbol: str
    condition: AlertCondition
    target_value: float = Field(..., description="Target price or percentage")
    current_price: Optional[float] = None
    status: AlertStatus = AlertStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.utcnow)
    triggered_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    message: Optional[str] = None


class Notification(BaseModel):
    """Notification to be sent to users."""
    id: Optional[str] = None
    user_id: str
    type: NotificationType
    title: str
    message: str
    symbol: Optional[str] = None
    data: Optional[dict[str, Any]] = None
    read: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)


class WebSocketMessage(BaseModel):
    """Message sent over WebSocket."""
    event: str
    data: dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class StockUpdate(BaseModel):
    """Real-time stock price update."""
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SubscriptionRequest(BaseModel):
    """Request to subscribe to stock updates."""
    symbols: list[str]
    include_sentiment: bool = False
    include_indicators: bool = False


class AlertCreateRequest(BaseModel):
    """Request to create a price alert."""
    symbol: str
    condition: AlertCondition
    target_value: float
    message: Optional[str] = None
    expires_in_days: Optional[int] = Field(None, ge=1, le=365)
