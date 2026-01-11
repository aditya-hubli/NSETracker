"""Data models for analytics service."""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class TimeFrame(str, Enum):
    """Time frame for analysis."""
    ONE_DAY = "1d"
    FIVE_DAYS = "5d"
    ONE_MONTH = "1mo"
    THREE_MONTHS = "3mo"
    SIX_MONTHS = "6mo"
    ONE_YEAR = "1y"
    TWO_YEARS = "2y"
    FIVE_YEARS = "5y"


class TechnicalIndicators(BaseModel):
    """Technical analysis indicators for a stock."""
    symbol: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Moving Averages
    sma_20: Optional[float] = Field(None, description="20-day Simple Moving Average")
    sma_50: Optional[float] = Field(None, description="50-day Simple Moving Average")
    sma_200: Optional[float] = Field(None, description="200-day Simple Moving Average")
    ema_12: Optional[float] = Field(None, description="12-day Exponential Moving Average")
    ema_26: Optional[float] = Field(None, description="26-day Exponential Moving Average")
    
    # MACD (Moving Average Convergence Divergence)
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    
    # RSI (Relative Strength Index)
    rsi_14: Optional[float] = Field(None, ge=0, le=100, description="14-day RSI")
    
    # Bollinger Bands
    bb_upper: Optional[float] = Field(None, description="Upper Bollinger Band")
    bb_middle: Optional[float] = Field(None, description="Middle Bollinger Band")
    bb_lower: Optional[float] = Field(None, description="Lower Bollinger Band")
    bb_width: Optional[float] = Field(None, description="Bollinger Band Width")
    
    # Volume indicators
    volume_sma_20: Optional[float] = Field(None, description="20-day Volume SMA")
    volume_ratio: Optional[float] = Field(None, description="Current volume / Average volume")
    
    # Volatility
    atr_14: Optional[float] = Field(None, description="14-day Average True Range")
    historical_volatility: Optional[float] = Field(None, description="Historical volatility %")
    
    # Support/Resistance
    support_level: Optional[float] = None
    resistance_level: Optional[float] = None
    
    # Current price for context
    current_price: Optional[float] = None


class SignalType(str, Enum):
    """Trading signal types."""
    STRONG_BUY = "strong_buy"
    BUY = "buy"
    NEUTRAL = "neutral"
    SELL = "sell"
    STRONG_SELL = "strong_sell"


class TradingSignal(BaseModel):
    """Trading signal based on technical analysis."""
    symbol: str
    signal: SignalType
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasons: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class VolumeAnalysis(BaseModel):
    """Volume analysis for a stock."""
    symbol: str
    current_volume: int
    average_volume_20d: float
    volume_ratio: float = Field(..., description="Current/Average ratio")
    is_unusual: bool = Field(..., description="Volume is 2x+ average")
    price_volume_correlation: Optional[float] = Field(
        None,
        ge=-1.0,
        le=1.0,
        description="Correlation between price and volume"
    )


class VolatilityMetrics(BaseModel):
    """Volatility metrics for a stock."""
    symbol: str
    historical_volatility_30d: float = Field(..., description="30-day historical volatility %")
    historical_volatility_90d: float = Field(..., description="90-day historical volatility %")
    atr_14: float = Field(..., description="14-day Average True Range")
    beta: Optional[float] = Field(None, description="Beta vs market")
    is_high_volatility: bool = Field(..., description="Volatility > 40%")


class PricePattern(str, Enum):
    """Chart pattern types."""
    DOUBLE_TOP = "double_top"
    DOUBLE_BOTTOM = "double_bottom"
    HEAD_SHOULDERS = "head_and_shoulders"
    INVERSE_HEAD_SHOULDERS = "inverse_head_and_shoulders"
    TRIANGLE_ASCENDING = "triangle_ascending"
    TRIANGLE_DESCENDING = "triangle_descending"
    BREAKOUT_UP = "breakout_up"
    BREAKOUT_DOWN = "breakout_down"
    CONSOLIDATION = "consolidation"


class PatternRecognition(BaseModel):
    """Detected chart patterns."""
    symbol: str
    pattern: PricePattern
    confidence: float = Field(..., ge=0.0, le=1.0)
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    price_target: Optional[float] = None
    description: str


class StockAnalysis(BaseModel):
    """Comprehensive technical analysis for a stock."""
    symbol: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    current_price: float
    indicators: TechnicalIndicators
    signal: TradingSignal
    volume_analysis: VolumeAnalysis
    volatility: VolatilityMetrics
    patterns: list[PatternRecognition] = Field(default_factory=list)
    key_levels: dict[str, float] = Field(
        default_factory=dict,
        description="Support/resistance levels"
    )


class ScreenerCriteria(BaseModel):
    """Criteria for stock screening."""
    # Price
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    
    # Volume
    min_volume: Optional[int] = None
    unusual_volume: Optional[bool] = None  # Volume > 2x average
    
    # Technical Indicators
    rsi_min: Optional[float] = Field(None, ge=0, le=100)
    rsi_max: Optional[float] = Field(None, ge=0, le=100)
    
    # Signals
    signals: Optional[list[SignalType]] = None
    
    # Volatility
    min_volatility: Optional[float] = None
    max_volatility: Optional[float] = None
    
    # Moving Average Crossovers
    golden_cross: Optional[bool] = None  # 50-day SMA crosses above 200-day
    death_cross: Optional[bool] = None   # 50-day SMA crosses below 200-day
    
    # Patterns
    patterns: Optional[list[PricePattern]] = None


class ScreenerResult(BaseModel):
    """Result from stock screener."""
    symbol: str
    company_name: Optional[str] = None
    price: float
    change_percent: float
    volume: int
    rsi: Optional[float] = None
    signal: SignalType
    matched_criteria: list[str] = Field(default_factory=list)
