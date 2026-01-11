"""Stock data models."""

from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field


class MarketStatus(str, Enum):
    """Market status enum."""
    
    OPEN = "open"
    CLOSED = "closed"
    PRE_MARKET = "pre_market"
    AFTER_HOURS = "after_hours"


class StockQuote(BaseModel):
    """Real-time stock quote."""
    
    symbol: str = Field(..., description="Stock ticker symbol")
    name: str = Field(..., description="Company name")
    price: Decimal = Field(..., description="Current price")
    change: Decimal = Field(..., description="Price change")
    change_percent: Decimal = Field(..., description="Percentage change")
    volume: int = Field(..., description="Trading volume")
    market_cap: Decimal | None = Field(None, description="Market capitalization")
    high: Decimal = Field(..., description="Day high")
    low: Decimal = Field(..., description="Day low")
    open: Decimal = Field(..., description="Opening price")
    previous_close: Decimal = Field(..., description="Previous close")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class StockHistoryPoint(BaseModel):
    """Historical price data point."""
    
    date: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int


class StockHistory(BaseModel):
    """Historical stock data."""
    
    symbol: str
    period: str  # 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max
    interval: str  # 1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo
    data: list[StockHistoryPoint]


class CompanyInfo(BaseModel):
    """Company information."""
    
    symbol: str
    name: str
    sector: str | None = None
    industry: str | None = None
    description: str | None = None
    website: str | None = None
    employees: int | None = None
    country: str | None = None
    exchange: str | None = None


class WatchlistCreate(BaseModel):
    """Create watchlist request."""
    
    user_id: str
    name: str = Field(..., min_length=1, max_length=100)
    symbols: list[str] = Field(default_factory=list)


class WatchlistUpdate(BaseModel):
    """Update watchlist request."""
    
    name: str | None = None
    symbols: list[str] | None = None


class Watchlist(BaseModel):
    """User watchlist."""
    
    id: str
    user_id: str
    name: str
    symbols: list[str]
    created_at: datetime
    updated_at: datetime


class WatchlistWithQuotes(BaseModel):
    """Watchlist with current stock quotes."""
    
    id: str
    user_id: str
    name: str
    stocks: list[StockQuote]
    created_at: datetime
    updated_at: datetime


class MarketSummary(BaseModel):
    """Market summary with major indices."""
    
    indices: list[StockQuote]
    market_status: MarketStatus
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TopMovers(BaseModel):
    """Top gaining and losing stocks."""
    
    gainers: list[StockQuote]
    losers: list[StockQuote]
    most_active: list[StockQuote]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
