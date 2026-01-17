"""Stock data provider using Yahoo Finance API."""

from datetime import datetime
from decimal import Decimal
from typing import Any

import yfinance as yf

from services.stock_service.models import (
    CompanyInfo,
    MarketStatus,
    MarketSummary,
    StockHistory,
    StockHistoryPoint,
    StockQuote,
    TopMovers,
)
from shared.logging_config import setup_logging

logger = setup_logging(service_name="stock-provider")

# Indian Market Indices (NSE/BSE)
MAJOR_INDICES = ["^NSEI", "^BSESN", "^NSEBANK", "^CNXIT"]  # NIFTY 50, SENSEX, Bank NIFTY, NIFTY IT
INDEX_NAMES = {
    "^NSEI": "NIFTY 50",
    "^BSESN": "SENSEX",
    "^NSEBANK": "Bank NIFTY",
    "^CNXIT": "NIFTY IT",
    "^CNXPHARMA": "NIFTY Pharma",
}

# Popular Indian stocks (NSE) - Top NIFTY 50 stocks
POPULAR_STOCKS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", 
    "HINDUNILVR.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS",
    "LT.NS", "AXISBANK.NS", "ASIANPAINT.NS", "MARUTI.NS", "SUNPHARMA.NS",
    "TITAN.NS", "BAJFINANCE.NS", "WIPRO.NS", "ULTRACEMCO.NS", "HCLTECH.NS",
    "TATAMOTORS.NS", "TATASTEEL.NS", "POWERGRID.NS", "NTPC.NS", "ONGC.NS",
    "ADANIENT.NS", "ADANIPORTS.NS", "JSWSTEEL.NS", "TECHM.NS", "INDUSINDBK.NS",
]

# Currency symbol for INR
CURRENCY_SYMBOL = "₹"


def _safe_decimal(value: Any, default: Decimal = Decimal("0")) -> Decimal:
    """Safely convert value to Decimal."""
    if value is None:
        return default
    try:
        if isinstance(value, (int, float)):
            return Decimal(str(value))
        return Decimal(value)
    except (ValueError, TypeError):
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    """Safely convert value to int."""
    if value is None:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


async def get_stock_quote(symbol: str) -> StockQuote | None:
    """Get real-time stock quote."""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        if not info or "regularMarketPrice" not in info:
            # Try fast_info for basic data
            fast = ticker.fast_info
            if hasattr(fast, "last_price") and fast.last_price:
                return StockQuote(
                    symbol=symbol.upper(),
                    name=info.get("shortName", symbol.upper()),
                    price=_safe_decimal(fast.last_price),
                    change=_safe_decimal(getattr(fast, "last_price", 0)) - _safe_decimal(getattr(fast, "previous_close", 0)),
                    change_percent=Decimal("0"),
                    volume=_safe_int(getattr(fast, "last_volume", 0)),
                    market_cap=_safe_decimal(getattr(fast, "market_cap", None)),
                    high=_safe_decimal(getattr(fast, "day_high", 0)),
                    low=_safe_decimal(getattr(fast, "day_low", 0)),
                    open=_safe_decimal(getattr(fast, "open", 0)),
                    previous_close=_safe_decimal(getattr(fast, "previous_close", 0)),
                )
            return None
        
        price = _safe_decimal(info.get("regularMarketPrice", 0))
        prev_close = _safe_decimal(info.get("regularMarketPreviousClose", info.get("previousClose", 0)))
        change = price - prev_close
        change_pct = (change / prev_close * 100) if prev_close else Decimal("0")
        
        return StockQuote(
            symbol=symbol.upper(),
            name=info.get("shortName", info.get("longName", symbol.upper())),
            price=price,
            change=change,
            change_percent=change_pct.quantize(Decimal("0.01")),
            volume=_safe_int(info.get("regularMarketVolume", info.get("volume", 0))),
            market_cap=_safe_decimal(info.get("marketCap")),
            high=_safe_decimal(info.get("regularMarketDayHigh", info.get("dayHigh", 0))),
            low=_safe_decimal(info.get("regularMarketDayLow", info.get("dayLow", 0))),
            open=_safe_decimal(info.get("regularMarketOpen", info.get("open", 0))),
            previous_close=prev_close,
        )
    except Exception as e:
        logger.error(f"Failed to get quote for {symbol}: {e}")
        return None


async def get_multiple_quotes(symbols: list[str]) -> list[StockQuote]:
    """Get quotes for multiple symbols."""
    quotes = []
    for symbol in symbols:
        quote = await get_stock_quote(symbol)
        if quote:
            quotes.append(quote)
    return quotes


async def get_stock_history(
    symbol: str,
    period: str = "1mo",
    interval: str = "1d"
) -> StockHistory | None:
    """Get historical stock data."""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period, interval=interval)
        
        if hist.empty:
            return None
        
        data_points = []
        for date, row in hist.iterrows():
            data_points.append(StockHistoryPoint(
                date=date.to_pydatetime(),
                open=_safe_decimal(row.get("Open", 0)),
                high=_safe_decimal(row.get("High", 0)),
                low=_safe_decimal(row.get("Low", 0)),
                close=_safe_decimal(row.get("Close", 0)),
                volume=_safe_int(row.get("Volume", 0)),
            ))
        
        return StockHistory(
            symbol=symbol.upper(),
            period=period,
            interval=interval,
            data=data_points,
        )
    except Exception as e:
        logger.error(f"Failed to get history for {symbol}: {e}")
        return None


async def get_company_info(symbol: str) -> CompanyInfo | None:
    """Get company information."""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        if not info:
            return None
        
        return CompanyInfo(
            symbol=symbol.upper(),
            name=info.get("shortName", info.get("longName", symbol.upper())),
            sector=info.get("sector"),
            industry=info.get("industry"),
            description=info.get("longBusinessSummary"),
            website=info.get("website"),
            employees=info.get("fullTimeEmployees"),
            country=info.get("country"),
            exchange=info.get("exchange"),
        )
    except Exception as e:
        logger.error(f"Failed to get company info for {symbol}: {e}")
        return None


async def get_market_summary() -> MarketSummary:
    """Get market summary with major indices."""
    indices = await get_multiple_quotes(MAJOR_INDICES)
    
    # Update names for indices
    for idx in indices:
        if idx.symbol in INDEX_NAMES:
            idx.name = INDEX_NAMES[idx.symbol]
    
    # Determine market status for Indian markets (NSE/BSE)
    # Market hours: 9:15 AM - 3:30 PM IST, Monday-Friday
    now = datetime.utcnow()
    
    # Convert UTC to IST (UTC + 5:30)
    utc_minutes = now.hour * 60 + now.minute
    ist_minutes = utc_minutes + 330  # Add 5 hours 30 minutes
    
    # Handle day rollover
    ist_day = now.weekday()
    if ist_minutes >= 1440:  # More than 24 hours worth of minutes
        ist_minutes -= 1440
        ist_day = (ist_day + 1) % 7
    
    market_open = 9 * 60 + 15   # 9:15 AM IST = 555 minutes
    market_close = 15 * 60 + 30  # 3:30 PM IST = 930 minutes
    pre_market_start = 9 * 60    # 9:00 AM IST
    
    if ist_day >= 5:  # Weekend (Saturday=5, Sunday=6)
        status = MarketStatus.CLOSED
    elif market_open <= ist_minutes <= market_close:
        status = MarketStatus.OPEN
    elif pre_market_start <= ist_minutes < market_open:
        status = MarketStatus.PRE_MARKET
    elif market_close < ist_minutes < market_close + 60:  # 1 hour after close
        status = MarketStatus.AFTER_HOURS
    else:
        status = MarketStatus.CLOSED
    
    return MarketSummary(
        indices=indices,
        market_status=status,
    )


async def get_top_movers() -> TopMovers:
    """Get top gaining, losing, and most active stocks."""
    quotes = await get_multiple_quotes(POPULAR_STOCKS)
    
    # Sort by change percent
    sorted_by_change = sorted(quotes, key=lambda x: x.change_percent, reverse=True)
    
    # Sort by volume
    sorted_by_volume = sorted(quotes, key=lambda x: x.volume, reverse=True)
    
    return TopMovers(
        gainers=sorted_by_change[:5],
        losers=sorted_by_change[-5:][::-1],
        most_active=sorted_by_volume[:5],
    )


async def search_stocks(query: str, limit: int = 20) -> list[dict]:
    """
    Search for NSE stocks by name or symbol.
    
    Args:
        query: Search query (symbol or company name)
        limit: Maximum results to return
        
    Returns:
        List of matching stocks with details
    """
    try:
        from services.stock_service.nse_stocks import search_nse_stocks, NSE_TOTAL_COUNT
        
        logger.info(f"Searching NSE stocks for: {query} (total NSE stocks: {NSE_TOTAL_COUNT})")
        
        # Get matching stocks from NSE list
        matches = search_nse_stocks(query, limit=limit)
        
        if not matches:
            return []
        
        results = []
        for match in matches:
            # Return basic info immediately (fast response)
            results.append({
                "symbol": match["symbol"],
                "name": match["name"],
                "price": None,  # Will be fetched on selection
                "change_percent": None,
            })
        
        return results
        
    except Exception as e:
        logger.error(f"Failed to search stocks: {e}")
        return []


async def search_stocks_with_quotes(query: str, limit: int = 10) -> list[dict]:
    """
    Search for NSE stocks and include live price quotes.
    Slower but provides real-time data.
    
    Args:
        query: Search query (symbol or company name)
        limit: Maximum results to return (kept small due to API calls)
        
    Returns:
        List of matching stocks with live price data
    """
    try:
        from services.stock_service.nse_stocks import search_nse_stocks
        
        matches = search_nse_stocks(query, limit=limit)
        
        if not matches:
            return []
        
        results = []
        for match in matches[:limit]:
            quote = await get_stock_quote(match["symbol"])
            if quote:
                results.append({
                    "symbol": quote.symbol,
                    "name": match["name"],
                    "price": str(quote.price),
                    "change_percent": str(quote.change_percent),
                })
            else:
                results.append({
                    "symbol": match["symbol"],
                    "name": match["name"],
                    "price": None,
                    "change_percent": None,
                })
        
        return results
        
    except Exception as e:
        logger.error(f"Failed to search stocks with quotes: {e}")
        return []
