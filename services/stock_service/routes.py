"""Stock service API routes."""

import asyncio
import json
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect

from services.stock_service.database import WatchlistRepository
from services.stock_service.models import (
    CompanyInfo,
    MarketSummary,
    StockHistory,
    StockQuote,
    TopMovers,
    Watchlist,
    WatchlistCreate,
    WatchlistUpdate,
    WatchlistWithQuotes,
)
from services.stock_service.provider import (
    get_company_info,
    get_market_summary,
    get_multiple_quotes,
    get_stock_history,
    get_stock_quote,
    get_top_movers,
    search_stocks,
)

router = APIRouter(prefix="/stocks", tags=["stocks"])
watchlist_repo = WatchlistRepository()


# ============== WebSocket Streaming with Fallback ==============

class StockStreamManager:
    """Manages WebSocket connections for stock streaming with Kafka fallback."""
    
    def __init__(self):
        self.active_connections: dict[WebSocket, set[str]] = {}
        self._kafka_consumer = None
        self._kafka_task: Optional[asyncio.Task] = None
        self._fallback_task: Optional[asyncio.Task] = None
        self._use_fallback = False
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[websocket] = set()
        
        # Start streaming if this is the first connection
        if len(self.active_connections) == 1:
            await self._start_streaming()
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.pop(websocket, None)
        
        # Stop streaming if no connections
        if not self.active_connections:
            self._stop_streaming()
    
    def subscribe(self, websocket: WebSocket, symbols: list[str]):
        if websocket in self.active_connections:
            self.active_connections[websocket].update(symbols)
    
    async def broadcast(self, message: dict):
        """Broadcast to all subscribed clients."""
        symbol = message.get("symbol", "")
        disconnected = []
        
        for ws, symbols in self.active_connections.items():
            if not symbols or symbol in symbols:
                try:
                    await ws.send_json(message)
                except Exception:
                    disconnected.append(ws)
        
        # Clean up disconnected clients
        for ws in disconnected:
            self.disconnect(ws)
    
    async def _start_streaming(self):
        """Start Kafka consumer or fallback to REST polling."""
        try:
            await self._start_kafka_consumer()
        except Exception as e:
            print(f"Kafka consumer failed, using fallback: {e}")
            self._use_fallback = True
            self._start_fallback_polling()
    
    async def _start_kafka_consumer(self):
        """Start consuming from Kafka."""
        from shared.config import get_settings
        from shared.events import get_kafka_ssl_context
        from aiokafka import AIOKafkaConsumer
        
        settings = get_settings()
        
        if settings.kafka_security_protocol == "PLAINTEXT" and "localhost" not in settings.kafka_brokers:
            raise Exception("Kafka not configured for cloud")
        
        ssl_context = get_kafka_ssl_context(settings)
        
        consumer_config = {
            "bootstrap_servers": settings.kafka_brokers,
            "group_id": f"websocket-stream-{id(self)}",
            "auto_offset_reset": "latest",
            "enable_auto_commit": True,
        }
        
        if ssl_context:
            consumer_config["security_protocol"] = settings.kafka_security_protocol
            consumer_config["ssl_context"] = ssl_context
        
        self._kafka_consumer = AIOKafkaConsumer("stock-prices", **consumer_config)
        await self._kafka_consumer.start()
        
        self._kafka_task = asyncio.create_task(self._consume_kafka())
    
    async def _consume_kafka(self):
        """Consume messages from Kafka and broadcast."""
        try:
            async for msg in self._kafka_consumer:
                try:
                    data = json.loads(msg.value.decode("utf-8"))
                    await self.broadcast(data)
                except json.JSONDecodeError:
                    continue
        except Exception as e:
            print(f"Kafka consumer error: {e}")
            # Switch to fallback
            self._use_fallback = True
            self._start_fallback_polling()
    
    def _start_fallback_polling(self):
        """Start REST API polling as fallback."""
        if self._fallback_task and not self._fallback_task.done():
            return
        self._fallback_task = asyncio.create_task(self._poll_prices())
    
    async def _poll_prices(self):
        """Poll stock prices via REST and broadcast."""
        default_symbols = ["TCS.NS", "RELIANCE.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS"]
        
        while self.active_connections:
            try:
                # Gather all subscribed symbols
                all_symbols = set()
                for symbols in self.active_connections.values():
                    all_symbols.update(symbols)
                
                if not all_symbols:
                    all_symbols = set(default_symbols)
                
                # Fetch quotes
                quotes = await get_multiple_quotes(list(all_symbols)[:20])
                
                # Broadcast each quote
                for quote in quotes:
                    await self.broadcast({
                        "type": "price_update",
                        "symbol": quote.symbol,
                        "price": float(quote.price),
                        "change": float(quote.change),
                        "change_percent": float(quote.change_percent),
                        "volume": quote.volume,
                        "timestamp": quote.timestamp,
                    })
                
                await asyncio.sleep(10)  # Poll every 10 seconds
            except Exception as e:
                print(f"Fallback polling error: {e}")
                await asyncio.sleep(5)
    
    def _stop_streaming(self):
        """Stop all streaming tasks."""
        if self._kafka_task:
            self._kafka_task.cancel()
        if self._fallback_task:
            self._fallback_task.cancel()
        if self._kafka_consumer:
            asyncio.create_task(self._kafka_consumer.stop())


# Global stream manager
stream_manager = StockStreamManager()


@router.websocket("/ws/stream")
async def websocket_stock_stream(websocket: WebSocket):
    """WebSocket endpoint for real-time stock streaming."""
    await stream_manager.connect(websocket)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "subscribe":
                symbols = data.get("symbols", [])
                stream_manager.subscribe(websocket, symbols)
                await websocket.send_json({"type": "subscribed", "symbols": symbols})
            
            elif data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        stream_manager.disconnect(websocket)
    except Exception:
        stream_manager.disconnect(websocket)


@router.get("/stream/status")
async def get_stream_status():
    """Get streaming status (Kafka or fallback)."""
    return {
        "active_connections": len(stream_manager.active_connections),
        "using_fallback": stream_manager._use_fallback,
        "mode": "fallback_polling" if stream_manager._use_fallback else "kafka_streaming",
    }


# ============== Stock Data Endpoints ==============


@router.get("/quote/{symbol}", response_model=StockQuote)
async def get_quote(symbol: str) -> StockQuote:
    """Get real-time stock quote."""
    quote = await get_stock_quote(symbol.upper())
    if not quote:
        raise HTTPException(status_code=404, detail=f"Stock {symbol} not found")
    return quote


@router.get("/quotes", response_model=list[StockQuote])
async def get_quotes(
    symbols: str = Query(..., description="Comma-separated list of symbols")
) -> list[StockQuote]:
    """Get quotes for multiple stocks."""
    symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
    if not symbol_list:
        raise HTTPException(status_code=400, detail="No symbols provided")
    if len(symbol_list) > 20:
        raise HTTPException(status_code=400, detail="Maximum 20 symbols allowed")
    return await get_multiple_quotes(symbol_list)


@router.get("/history/{symbol}", response_model=StockHistory)
async def get_history(
    symbol: str,
    period: str = Query("1mo", description="Period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max"),
    interval: str = Query("1d", description="Interval: 1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo"),
) -> StockHistory:
    """Get historical stock data."""
    valid_periods = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "max"]
    valid_intervals = ["1m", "5m", "15m", "30m", "1h", "1d", "1wk", "1mo"]
    
    if period not in valid_periods:
        raise HTTPException(status_code=400, detail=f"Invalid period. Must be one of: {valid_periods}")
    if interval not in valid_intervals:
        raise HTTPException(status_code=400, detail=f"Invalid interval. Must be one of: {valid_intervals}")
    
    history = await get_stock_history(symbol.upper(), period, interval)
    if not history:
        raise HTTPException(status_code=404, detail=f"No history found for {symbol}")
    return history


@router.get("/company/{symbol}", response_model=CompanyInfo)
async def get_company(symbol: str) -> CompanyInfo:
    """Get company information."""
    info = await get_company_info(symbol.upper())
    if not info:
        raise HTTPException(status_code=404, detail=f"Company {symbol} not found")
    return info


@router.get("/market/summary", response_model=MarketSummary)
async def market_summary() -> MarketSummary:
    """Get market summary with major indices."""
    return await get_market_summary()


@router.get("/market/movers", response_model=TopMovers)
async def top_movers() -> TopMovers:
    """Get top gaining, losing, and most active stocks."""
    return await get_top_movers()


@router.get("/search")
async def search(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=50),
    include_quotes: bool = Query(False, description="Include live price quotes (slower)"),
) -> list[dict]:
    """
    Search for NSE stocks by name or symbol.
    
    Set include_quotes=true to get live prices (slower, limited results).
    """
    if include_quotes:
        from services.stock_service.provider import search_stocks_with_quotes
        return await search_stocks_with_quotes(q, min(limit, 10))
    return await search_stocks(q, limit)


@router.get("/nse/all")
async def get_all_nse_stocks() -> dict:
    """Get list of all available NSE stocks."""
    from services.stock_service.nse_stocks import (
        NIFTY_50, NIFTY_NEXT_50, OTHER_NSE_STOCKS, 
        NSE_STOCK_NAMES, NSE_TOTAL_COUNT
    )
    
    return {
        "total_count": NSE_TOTAL_COUNT,
        "nifty_50": [{"symbol": f"{s}.NS", "name": NSE_STOCK_NAMES.get(s, s)} for s in NIFTY_50],
        "nifty_next_50": [{"symbol": f"{s}.NS", "name": NSE_STOCK_NAMES.get(s, s)} for s in NIFTY_NEXT_50],
        "categories": {
            "nifty_50": len(NIFTY_50),
            "nifty_next_50": len(NIFTY_NEXT_50),
            "others": len(OTHER_NSE_STOCKS),
        }
    }


@router.get("/nse/sectors")
async def get_nse_sectors() -> dict:
    """Get NSE stocks organized by sector."""
    return {
        "sectors": [
            {"name": "Banking & Finance", "stocks": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS", "BAJFINANCE.NS"]},
            {"name": "IT & Technology", "stocks": ["TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS", "LTIM.NS"]},
            {"name": "Oil & Gas", "stocks": ["RELIANCE.NS", "ONGC.NS", "BPCL.NS", "IOC.NS", "GAIL.NS"]},
            {"name": "Pharma & Healthcare", "stocks": ["SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS", "DIVISLAB.NS", "APOLLOHOSP.NS"]},
            {"name": "Auto & Auto Parts", "stocks": ["TATAMOTORS.NS", "MARUTI.NS", "BAJAJ-AUTO.NS", "M&M.NS", "HEROMOTOCO.NS"]},
            {"name": "FMCG", "stocks": ["HINDUNILVR.NS", "ITC.NS", "BRITANNIA.NS", "NESTLEIND.NS", "DABUR.NS"]},
            {"name": "Metals & Mining", "stocks": ["TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "VEDL.NS", "NMDC.NS"]},
            {"name": "Infrastructure", "stocks": ["LT.NS", "ADANIPORTS.NS", "ADANIENT.NS", "POWERGRID.NS", "NTPC.NS"]},
            {"name": "Real Estate", "stocks": ["DLF.NS", "GODREJPROP.NS", "OBEROIRLTY.NS", "PRESTIGE.NS"]},
            {"name": "Telecom", "stocks": ["BHARTIARTL.NS", "IDEA.NS"]},
        ]
    }


# ============== Watchlist Endpoints ==============


@router.post("/watchlists", response_model=Watchlist, status_code=201)
async def create_watchlist(data: WatchlistCreate) -> Watchlist:
    """Create a new watchlist."""
    watchlist_data = {
        "user_id": data.user_id,
        "name": data.name,
        "symbols": [s.upper() for s in data.symbols],
    }
    result = await watchlist_repo.create_watchlist(watchlist_data)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to create watchlist")
    return Watchlist(**result)


@router.get("/watchlists/user/{user_id}", response_model=list[Watchlist])
async def get_user_watchlists(user_id: str) -> list[Watchlist]:
    """Get all watchlists for a user."""
    watchlists = await watchlist_repo.get_user_watchlists(user_id)
    return [Watchlist(**w) for w in watchlists]


@router.get("/watchlists/{watchlist_id}", response_model=Watchlist)
async def get_watchlist(watchlist_id: str) -> Watchlist:
    """Get a watchlist by ID."""
    result = await watchlist_repo.get_watchlist(watchlist_id)
    if not result:
        raise HTTPException(status_code=404, detail="Watchlist not found")
    return Watchlist(**result)


@router.get("/watchlists/{watchlist_id}/quotes", response_model=WatchlistWithQuotes)
async def get_watchlist_with_quotes(watchlist_id: str) -> WatchlistWithQuotes:
    """Get a watchlist with current stock quotes."""
    watchlist = await watchlist_repo.get_watchlist(watchlist_id)
    if not watchlist:
        raise HTTPException(status_code=404, detail="Watchlist not found")
    
    quotes = await get_multiple_quotes(watchlist.get("symbols", []))
    
    return WatchlistWithQuotes(
        id=watchlist["id"],
        user_id=watchlist["user_id"],
        name=watchlist["name"],
        stocks=quotes,
        created_at=watchlist["created_at"],
        updated_at=watchlist["updated_at"],
    )


@router.put("/watchlists/{watchlist_id}", response_model=Watchlist)
async def update_watchlist(watchlist_id: str, data: WatchlistUpdate) -> Watchlist:
    """Update a watchlist."""
    update_data = {}
    if data.name is not None:
        update_data["name"] = data.name
    if data.symbols is not None:
        update_data["symbols"] = [s.upper() for s in data.symbols]
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No update data provided")
    
    result = await watchlist_repo.update_watchlist(watchlist_id, update_data)
    if not result:
        raise HTTPException(status_code=404, detail="Watchlist not found")
    return Watchlist(**result)


@router.delete("/watchlists/{watchlist_id}", status_code=204)
async def delete_watchlist(watchlist_id: str) -> None:
    """Delete a watchlist."""
    success = await watchlist_repo.delete_watchlist(watchlist_id)
    if not success:
        raise HTTPException(status_code=404, detail="Watchlist not found")


@router.post("/watchlists/{watchlist_id}/symbols/{symbol}", response_model=Watchlist)
async def add_symbol(watchlist_id: str, symbol: str) -> Watchlist:
    """Add a symbol to a watchlist."""
    result = await watchlist_repo.add_symbol_to_watchlist(watchlist_id, symbol.upper())
    if not result:
        raise HTTPException(status_code=404, detail="Watchlist not found")
    return Watchlist(**result)


@router.delete("/watchlists/{watchlist_id}/symbols/{symbol}", response_model=Watchlist)
async def remove_symbol(watchlist_id: str, symbol: str) -> Watchlist:
    """Remove a symbol from a watchlist."""
    result = await watchlist_repo.remove_symbol_from_watchlist(watchlist_id, symbol.upper())
    if not result:
        raise HTTPException(status_code=404, detail="Watchlist not found")
    return Watchlist(**result)
