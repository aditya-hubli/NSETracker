"""WebSocket connection manager for real-time updates."""
import asyncio
import json
from datetime import datetime
from typing import Optional

from fastapi import WebSocket
import yfinance as yf

from .models import StockUpdate, WebSocketMessage


class ConnectionManager:
    """Manage WebSocket connections and subscriptions."""
    
    def __init__(self):
        # user_id -> WebSocket
        self.active_connections: dict[str, WebSocket] = {}
        # user_id -> set of symbols
        self.subscriptions: dict[str, set[str]] = {}
        # symbol -> set of user_ids
        self.symbol_subscribers: dict[str, set[str]] = {}
        # Background task reference
        self._update_task: Optional[asyncio.Task] = None
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.subscriptions[user_id] = set()
        print(f"User {user_id} connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, user_id: str):
        """Handle disconnection."""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        
        # Clean up subscriptions
        if user_id in self.subscriptions:
            for symbol in self.subscriptions[user_id]:
                if symbol in self.symbol_subscribers:
                    self.symbol_subscribers[symbol].discard(user_id)
            del self.subscriptions[user_id]
        
        print(f"User {user_id} disconnected. Total connections: {len(self.active_connections)}")
    
    async def subscribe(self, user_id: str, symbols: list[str]):
        """Subscribe user to stock updates."""
        if user_id not in self.subscriptions:
            self.subscriptions[user_id] = set()
        
        for symbol in symbols:
            symbol = symbol.upper()
            self.subscriptions[user_id].add(symbol)
            
            if symbol not in self.symbol_subscribers:
                self.symbol_subscribers[symbol] = set()
            self.symbol_subscribers[symbol].add(user_id)
        
        # Send confirmation
        await self.send_personal_message(
            user_id,
            WebSocketMessage(
                event="subscribed",
                data={"symbols": list(self.subscriptions[user_id])}
            )
        )
    
    async def unsubscribe(self, user_id: str, symbols: list[str]):
        """Unsubscribe user from stock updates."""
        if user_id not in self.subscriptions:
            return
        
        for symbol in symbols:
            symbol = symbol.upper()
            self.subscriptions[user_id].discard(symbol)
            
            if symbol in self.symbol_subscribers:
                self.symbol_subscribers[symbol].discard(user_id)
    
    async def send_personal_message(self, user_id: str, message: WebSocketMessage):
        """Send message to specific user."""
        if user_id in self.active_connections:
            try:
                websocket = self.active_connections[user_id]
                await websocket.send_json(message.model_dump(mode="json"))
            except Exception as e:
                print(f"Error sending to {user_id}: {e}")
                self.disconnect(user_id)
    
    async def broadcast_to_subscribers(self, symbol: str, message: WebSocketMessage):
        """Broadcast message to all subscribers of a symbol."""
        symbol = symbol.upper()
        if symbol not in self.symbol_subscribers:
            return
        
        for user_id in self.symbol_subscribers[symbol].copy():
            await self.send_personal_message(user_id, message)
    
    async def broadcast_all(self, message: WebSocketMessage):
        """Broadcast to all connected users."""
        for user_id in list(self.active_connections.keys()):
            await self.send_personal_message(user_id, message)
    
    def get_all_subscribed_symbols(self) -> set[str]:
        """Get all symbols with active subscribers."""
        return set(self.symbol_subscribers.keys())
    
    async def start_price_updates(self, interval_seconds: int = 5):
        """Start background task for price updates."""
        if self._update_task is None or self._update_task.done():
            self._update_task = asyncio.create_task(
                self._price_update_loop(interval_seconds)
            )
    
    async def stop_price_updates(self):
        """Stop background price updates."""
        if self._update_task:
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass
    
    async def _price_update_loop(self, interval: int):
        """Background loop to fetch and broadcast price updates."""
        while True:
            try:
                symbols = self.get_all_subscribed_symbols()
                
                if symbols:
                    # Batch fetch prices
                    updates = await self._fetch_prices(list(symbols))
                    
                    for update in updates:
                        message = WebSocketMessage(
                            event="price_update",
                            data=update.model_dump(mode="json")
                        )
                        await self.broadcast_to_subscribers(update.symbol, message)
                
                await asyncio.sleep(interval)
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in price update loop: {e}")
                await asyncio.sleep(interval)
    
    async def _fetch_prices(self, symbols: list[str]) -> list[StockUpdate]:
        """Fetch current prices for symbols."""
        updates = []
        
        try:
            # Batch fetch using yfinance
            tickers = yf.Tickers(" ".join(symbols))
            
            for symbol in symbols:
                try:
                    ticker = tickers.tickers.get(symbol)
                    if ticker:
                        info = ticker.fast_info
                        
                        price = info.last_price
                        prev_close = info.previous_close
                        change = price - prev_close
                        change_percent = (change / prev_close) * 100 if prev_close else 0
                        
                        updates.append(StockUpdate(
                            symbol=symbol,
                            price=price,
                            change=change,
                            change_percent=change_percent,
                            volume=info.last_volume or 0
                        ))
                except Exception as e:
                    print(f"Error fetching {symbol}: {e}")
        
        except Exception as e:
            print(f"Error batch fetching prices: {e}")
        
        return updates


# Global connection manager instance
manager = ConnectionManager()
