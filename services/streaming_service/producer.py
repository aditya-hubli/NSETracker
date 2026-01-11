"""Stock price producer - fetches prices and publishes to Redpanda."""

import asyncio
from datetime import datetime
from typing import Optional

import yfinance as yf
from aiokafka import AIOKafkaProducer
import json

from shared.config import get_settings

# Top Indian stocks to stream by default
DEFAULT_SYMBOLS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "HINDUNILVR.NS", "SBIN.NS", "BHARTIARTL.NS", "BAJFINANCE.NS", "KOTAKBANK.NS",
    "ITC.NS", "LT.NS", "AXISBANK.NS", "ASIANPAINT.NS", "MARUTI.NS",
    "HCLTECH.NS", "WIPRO.NS", "SUNPHARMA.NS", "ULTRACEMCO.NS", "TITAN.NS",
]

TOPIC_STOCK_PRICES = "stock-prices"


class StockPriceProducer:
    """Produces real-time stock prices to Redpanda/Kafka."""
    
    def __init__(self, symbols: Optional[list[str]] = None):
        self.symbols = symbols or DEFAULT_SYMBOLS
        self.settings = get_settings()
        self._producer: Optional[AIOKafkaProducer] = None
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._price_cache: dict[str, float] = {}
    
    async def start(self) -> bool:
        """Start the producer and streaming loop."""
        try:
            self._producer = AIOKafkaProducer(
                bootstrap_servers=self.settings.kafka_brokers,
                value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
            )
            await self._producer.start()
            self._running = True
            print(f"Stock price producer connected to {self.settings.kafka_brokers}")
            
            # Start streaming loop
            self._task = asyncio.create_task(self._stream_loop())
            return True
            
        except Exception as e:
            print(f"Failed to start producer: {e}")
            return False
    
    async def stop(self) -> None:
        """Stop the producer."""
        self._running = False
        
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        if self._producer:
            await self._producer.stop()
            self._producer = None
            print("Stock price producer stopped")
    
    def add_symbols(self, symbols: list[str]) -> None:
        """Add symbols to stream."""
        for symbol in symbols:
            if symbol.upper() not in self.symbols:
                self.symbols.append(symbol.upper())
    
    def remove_symbols(self, symbols: list[str]) -> None:
        """Remove symbols from stream."""
        for symbol in symbols:
            if symbol.upper() in self.symbols:
                self.symbols.remove(symbol.upper())
    
    async def _stream_loop(self, interval: int = 5) -> None:
        """Main loop to fetch and publish prices."""
        print(f"Starting price stream for {len(self.symbols)} symbols, interval={interval}s")
        
        while self._running:
            try:
                await self._fetch_and_publish()
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in stream loop: {e}")
                await asyncio.sleep(interval)
    
    async def _fetch_and_publish(self) -> None:
        """Fetch current prices and publish to Kafka."""
        if not self.symbols or not self._producer:
            return
        
        try:
            # Batch fetch prices using yfinance
            tickers = yf.Tickers(" ".join(self.symbols))
            
            for symbol in self.symbols:
                try:
                    ticker = tickers.tickers.get(symbol)
                    if not ticker:
                        continue
                    
                    info = ticker.fast_info
                    price = info.last_price
                    prev_close = info.previous_close or price
                    
                    # Skip if price unchanged
                    if self._price_cache.get(symbol) == price:
                        continue
                    
                    self._price_cache[symbol] = price
                    
                    change = price - prev_close
                    change_percent = (change / prev_close * 100) if prev_close else 0
                    
                    message = {
                        "event": "price_update",
                        "symbol": symbol,
                        "price": round(price, 2),
                        "change": round(change, 2),
                        "change_percent": round(change_percent, 2),
                        "volume": info.last_volume or 0,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                    
                    await self._producer.send_and_wait(
                        TOPIC_STOCK_PRICES,
                        value=message,
                        key=symbol
                    )
                    
                except Exception as e:
                    print(f"Error fetching {symbol}: {e}")
                    
        except Exception as e:
            print(f"Error in batch fetch: {e}")


# Global producer instance
_producer: Optional[StockPriceProducer] = None


async def start_producer(symbols: Optional[list[str]] = None) -> bool:
    """Start the global stock price producer."""
    global _producer
    
    if _producer is not None:
        return True
    
    _producer = StockPriceProducer(symbols)
    return await _producer.start()


async def stop_producer() -> None:
    """Stop the global stock price producer."""
    global _producer
    
    if _producer:
        await _producer.stop()
        _producer = None


def get_producer() -> Optional[StockPriceProducer]:
    """Get the global producer instance."""
    return _producer
