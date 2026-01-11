"""API routes for analytics service."""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from .models import (
    TechnicalIndicators,
    TradingSignal,
    VolumeAnalysis,
    VolatilityMetrics,
    StockAnalysis,
    ScreenerCriteria,
    ScreenerResult,
    SignalType,
    TimeFrame,
)
from .calculator import TechnicalAnalyzer

router = APIRouter(prefix="/analytics", tags=["analytics"])

# Initialize analyzer
analyzer = TechnicalAnalyzer()


@router.get("/indicators/{symbol}", response_model=TechnicalIndicators)
async def get_technical_indicators(
    symbol: str,
    period: str = Query("1y", pattern="^(1mo|3mo|6mo|1y|2y|5y)$")
):
    """
    Get all technical indicators for a stock.
    
    Returns:
    - Moving Averages (SMA 20/50/200, EMA 12/26)
    - MACD and Signal Line
    - RSI (14-day)
    - Bollinger Bands
    - Volume indicators
    - ATR and Volatility
    - Support/Resistance levels
    """
    symbol = symbol.upper()
    
    df = analyzer.get_stock_data(symbol, period=period)
    if df is None:
        raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
    
    indicators = analyzer.calculate_indicators(symbol, df)
    if indicators is None:
        raise HTTPException(status_code=500, detail="Error calculating indicators")
    
    return indicators


@router.get("/signal/{symbol}", response_model=TradingSignal)
async def get_trading_signal(symbol: str):
    """
    Get trading signal based on technical analysis.
    
    Analyzes multiple indicators and returns:
    - Signal: STRONG_BUY, BUY, NEUTRAL, SELL, STRONG_SELL
    - Confidence score (0-1)
    - Reasons for the signal
    """
    symbol = symbol.upper()
    
    df = analyzer.get_stock_data(symbol)
    if df is None:
        raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
    
    indicators = analyzer.calculate_indicators(symbol, df)
    if indicators is None:
        raise HTTPException(status_code=500, detail="Error calculating indicators")
    
    signal = analyzer.generate_signal(symbol, indicators, df)
    return signal


@router.get("/volume/{symbol}", response_model=VolumeAnalysis)
async def get_volume_analysis(symbol: str):
    """
    Analyze volume patterns for a stock.
    
    Returns:
    - Current volume
    - 20-day average volume
    - Volume ratio (current/average)
    - Unusual volume flag
    - Price-volume correlation
    """
    symbol = symbol.upper()
    
    volume = analyzer.analyze_volume(symbol)
    if volume is None:
        raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
    
    return volume


@router.get("/volatility/{symbol}", response_model=VolatilityMetrics)
async def get_volatility_metrics(symbol: str):
    """
    Get volatility metrics for a stock.
    
    Returns:
    - 30-day historical volatility
    - 90-day historical volatility
    - ATR (14-day)
    - High volatility flag
    """
    symbol = symbol.upper()
    
    volatility = analyzer.analyze_volatility(symbol)
    if volatility is None:
        raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
    
    return volatility


@router.get("/analysis/{symbol}", response_model=StockAnalysis)
async def get_full_analysis(symbol: str):
    """
    Get comprehensive technical analysis for a stock.
    
    Includes all indicators, signals, volume analysis,
    volatility metrics, and pattern recognition.
    """
    symbol = symbol.upper()
    
    df = analyzer.get_stock_data(symbol)
    if df is None:
        raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
    
    indicators = analyzer.calculate_indicators(symbol, df)
    if indicators is None:
        raise HTTPException(status_code=500, detail="Error calculating indicators")
    
    signal = analyzer.generate_signal(symbol, indicators, df)
    volume = analyzer.analyze_volume(symbol, df)
    volatility = analyzer.analyze_volatility(symbol, df)
    patterns = analyzer.detect_patterns(symbol, df)
    
    return StockAnalysis(
        symbol=symbol,
        current_price=indicators.current_price,
        indicators=indicators,
        signal=signal,
        volume_analysis=volume,
        volatility=volatility,
        patterns=patterns,
        key_levels={
            "support": indicators.support_level,
            "resistance": indicators.resistance_level,
            "sma_20": indicators.sma_20,
            "sma_50": indicators.sma_50,
            "sma_200": indicators.sma_200,
        }
    )


@router.post("/screener", response_model=list[ScreenerResult])
async def screen_stocks(
    criteria: ScreenerCriteria,
    symbols: list[str] = Query(
        default=["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "JPM", "V", "WMT"],
        description="List of symbols to screen"
    )
):
    """
    Screen stocks based on technical criteria.
    
    Filter stocks by:
    - Price range
    - Volume (minimum, unusual)
    - RSI range (oversold/overbought)
    - Signals (BUY, SELL, etc.)
    - Volatility
    - Moving average crossovers
    """
    results = []
    
    for symbol in symbols:
        try:
            symbol = symbol.upper()
            df = analyzer.get_stock_data(symbol, period="3mo")
            
            if df is None or df.empty:
                continue
            
            indicators = analyzer.calculate_indicators(symbol, df)
            if indicators is None:
                continue
            
            signal = analyzer.generate_signal(symbol, indicators, df)
            
            # Get current data
            current_price = float(df['Close'].iloc[-1])
            prev_close = float(df['Close'].iloc[-2])
            change_percent = ((current_price - prev_close) / prev_close) * 100
            volume = int(df['Volume'].iloc[-1])
            
            # Check criteria matches
            matched = []
            skip = False
            
            # Price filter
            if criteria.min_price and current_price < criteria.min_price:
                skip = True
            if criteria.max_price and current_price > criteria.max_price:
                skip = True
            
            # Volume filter
            if criteria.min_volume and volume < criteria.min_volume:
                skip = True
            if criteria.unusual_volume and indicators.volume_ratio:
                if indicators.volume_ratio >= 2.0:
                    matched.append("Unusual volume")
                elif criteria.unusual_volume:
                    skip = True
            
            # RSI filter
            if indicators.rsi_14:
                if criteria.rsi_min and indicators.rsi_14 < criteria.rsi_min:
                    skip = True
                if criteria.rsi_max and indicators.rsi_14 > criteria.rsi_max:
                    skip = True
                if indicators.rsi_14 < 30:
                    matched.append("RSI oversold")
                elif indicators.rsi_14 > 70:
                    matched.append("RSI overbought")
            
            # Signal filter
            if criteria.signals and signal.signal not in criteria.signals:
                skip = True
            else:
                matched.append(f"Signal: {signal.signal.value}")
            
            # Volatility filter
            if indicators.historical_volatility:
                if criteria.min_volatility and indicators.historical_volatility < criteria.min_volatility:
                    skip = True
                if criteria.max_volatility and indicators.historical_volatility > criteria.max_volatility:
                    skip = True
            
            # Golden/Death cross
            if indicators.sma_50 and indicators.sma_200:
                is_golden = indicators.sma_50 > indicators.sma_200
                is_death = indicators.sma_50 < indicators.sma_200
                
                if criteria.golden_cross:
                    if is_golden:
                        matched.append("Golden cross")
                    else:
                        skip = True
                
                if criteria.death_cross:
                    if is_death:
                        matched.append("Death cross")
                    else:
                        skip = True
            
            if skip:
                continue
            
            results.append(ScreenerResult(
                symbol=symbol,
                price=current_price,
                change_percent=change_percent,
                volume=volume,
                rsi=indicators.rsi_14,
                signal=signal.signal,
                matched_criteria=matched
            ))
        
        except Exception as e:
            print(f"Error screening {symbol}: {e}")
            continue
    
    # Sort by signal strength
    signal_order = {
        SignalType.STRONG_BUY: 0,
        SignalType.BUY: 1,
        SignalType.NEUTRAL: 2,
        SignalType.SELL: 3,
        SignalType.STRONG_SELL: 4
    }
    results.sort(key=lambda x: signal_order.get(x.signal, 2))
    
    return results


@router.get("/heatmap")
async def get_market_heatmap(
    symbols: list[str] = Query(
        default=[
            "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA",
            "JPM", "V", "WMT", "JNJ", "PG", "XOM", "CVX", "BAC"
        ],
        description="List of symbols for heatmap"
    )
):
    """
    Get market heatmap data for visualization.
    
    Returns price changes and volume data for creating
    a market heatmap visualization.
    """
    heatmap_data = []
    
    for symbol in symbols:
        try:
            symbol = symbol.upper()
            df = analyzer.get_stock_data(symbol, period="5d")
            
            if df is None or df.empty:
                continue
            
            current_price = float(df['Close'].iloc[-1])
            prev_close = float(df['Close'].iloc[-2])
            change_percent = ((current_price - prev_close) / prev_close) * 100
            volume = int(df['Volume'].iloc[-1])
            avg_volume = float(df['Volume'].mean())
            
            heatmap_data.append({
                "symbol": symbol,
                "price": current_price,
                "change_percent": round(change_percent, 2),
                "volume": volume,
                "volume_ratio": round(volume / avg_volume, 2) if avg_volume > 0 else 0,
                "color": "green" if change_percent >= 0 else "red",
                "intensity": min(abs(change_percent) / 5.0, 1.0)  # Normalize to 0-1
            })
        
        except Exception as e:
            print(f"Error getting heatmap data for {symbol}: {e}")
            continue
    
    return heatmap_data
