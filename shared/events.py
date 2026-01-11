"""Event streaming with Kafka/Redpanda for real-time data processing."""
import asyncio
import json
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from pydantic import BaseModel, Field

from .config import get_settings


class EventType(str, Enum):
    """Types of events in the system."""
    # Stock Events
    STOCK_PRICE_UPDATE = "stock.price.update"
    STOCK_VOLUME_SPIKE = "stock.volume.spike"
    STOCK_SIGNAL_CHANGE = "stock.signal.change"
    
    # Sentiment Events
    SENTIMENT_UPDATE = "sentiment.update"
    SENTIMENT_SHIFT = "sentiment.shift"
    
    # Alert Events
    ALERT_TRIGGERED = "alert.triggered"
    ALERT_CREATED = "alert.created"
    
    # User Events
    USER_WATCHLIST_UPDATE = "user.watchlist.update"
    USER_NOTIFICATION = "user.notification"
    
    # System Events
    SYSTEM_HEALTH = "system.health"
    SYSTEM_ERROR = "system.error"


class Event(BaseModel):
    """Base event model for streaming."""
    event_type: EventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source_service: str
    correlation_id: Optional[str] = None
    data: dict[str, Any]
    
    def to_json(self) -> str:
        """Serialize event to JSON."""
        return self.model_dump_json()
    
    @classmethod
    def from_json(cls, data: str) -> "Event":
        """Deserialize event from JSON."""
        return cls.model_validate_json(data)


class EventProducer:
    """Kafka/Redpanda event producer."""
    
    def __init__(self):
        self._producer: Optional[AIOKafkaProducer] = None
        self._settings = get_settings()
    
    async def start(self) -> None:
        """Start the producer."""
        if self._producer is None:
            self._producer = AIOKafkaProducer(
                bootstrap_servers=self._settings.kafka_brokers,
                value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
            )
            await self._producer.start()
            print(f"Event producer started, connected to {self._settings.kafka_brokers}")
    
    async def stop(self) -> None:
        """Stop the producer."""
        if self._producer:
            await self._producer.stop()
            self._producer = None
            print("Event producer stopped")
    
    async def send(
        self,
        topic: str,
        event: Event,
        key: Optional[str] = None
    ) -> None:
        """Send an event to a topic."""
        if not self._producer:
            raise RuntimeError("Producer not started")
        
        await self._producer.send_and_wait(
            topic,
            value=event.model_dump(mode="json"),
            key=key
        )
    
    async def send_stock_update(
        self,
        symbol: str,
        price: float,
        change: float,
        change_percent: float,
        volume: int
    ) -> None:
        """Send stock price update event."""
        event = Event(
            event_type=EventType.STOCK_PRICE_UPDATE,
            source_service="stock_service",
            data={
                "symbol": symbol,
                "price": price,
                "change": change,
                "change_percent": change_percent,
                "volume": volume,
            }
        )
        await self.send("stock-updates", event, key=symbol)
    
    async def send_sentiment_update(
        self,
        symbol: str,
        score: float,
        classification: str,
        sources: dict[str, float]
    ) -> None:
        """Send sentiment update event."""
        event = Event(
            event_type=EventType.SENTIMENT_UPDATE,
            source_service="sentiment_service",
            data={
                "symbol": symbol,
                "score": score,
                "classification": classification,
                "sources": sources,
            }
        )
        await self.send("sentiment-updates", event, key=symbol)
    
    async def send_alert_triggered(
        self,
        user_id: str,
        alert_id: str,
        symbol: str,
        condition: str,
        target_value: float,
        current_price: float
    ) -> None:
        """Send alert triggered event."""
        event = Event(
            event_type=EventType.ALERT_TRIGGERED,
            source_service="notification_service",
            data={
                "user_id": user_id,
                "alert_id": alert_id,
                "symbol": symbol,
                "condition": condition,
                "target_value": target_value,
                "current_price": current_price,
            }
        )
        await self.send("alerts", event, key=user_id)


class EventConsumer:
    """Kafka/Redpanda event consumer."""
    
    def __init__(self, group_id: Optional[str] = None):
        self._consumer: Optional[AIOKafkaConsumer] = None
        self._settings = get_settings()
        self._group_id = group_id or self._settings.kafka_consumer_group
        self._handlers: dict[EventType, list[Callable]] = {}
        self._running = False
    
    def register_handler(
        self,
        event_type: EventType,
        handler: Callable[[Event], Any]
    ) -> None:
        """Register a handler for an event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    async def start(self, topics: list[str]) -> None:
        """Start consuming from topics."""
        if self._consumer is None:
            self._consumer = AIOKafkaConsumer(
                *topics,
                bootstrap_servers=self._settings.kafka_brokers,
                group_id=self._group_id,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='latest',
            )
            await self._consumer.start()
            self._running = True
            print(f"Event consumer started, subscribed to {topics}")
    
    async def stop(self) -> None:
        """Stop the consumer."""
        self._running = False
        if self._consumer:
            await self._consumer.stop()
            self._consumer = None
            print("Event consumer stopped")
    
    async def consume(self) -> None:
        """Main consume loop."""
        if not self._consumer:
            raise RuntimeError("Consumer not started")
        
        try:
            async for msg in self._consumer:
                if not self._running:
                    break
                
                try:
                    # Parse event
                    event = Event.model_validate(msg.value)
                    
                    # Call registered handlers
                    handlers = self._handlers.get(event.event_type, [])
                    for handler in handlers:
                        try:
                            if asyncio.iscoroutinefunction(handler):
                                await handler(event)
                            else:
                                handler(event)
                        except Exception as e:
                            print(f"Handler error for {event.event_type}: {e}")
                
                except Exception as e:
                    print(f"Error processing message: {e}")
        
        except asyncio.CancelledError:
            pass


# ==================== Topic Configuration ====================

TOPICS = {
    "stock-updates": "Real-time stock price updates",
    "sentiment-updates": "Sentiment analysis updates",
    "alerts": "User alert triggers",
    "notifications": "User notifications",
    "analytics": "Analytics and signals",
    "system": "System events and health checks",
}


async def create_topics(admin_client=None) -> None:
    """Create required Kafka topics (if using admin client)."""
    # This would use Kafka AdminClient to create topics
    # For Redpanda, topics are auto-created by default
    pass


# ==================== Stream Processors ====================

class StockUpdateProcessor:
    """Process stock update events."""
    
    def __init__(self):
        self.price_cache: dict[str, float] = {}
    
    async def process(self, event: Event) -> None:
        """Process a stock update event."""
        data = event.data
        symbol = data["symbol"]
        price = data["price"]
        
        # Track price changes
        old_price = self.price_cache.get(symbol)
        self.price_cache[symbol] = price
        
        # Detect significant movements
        if old_price and abs((price - old_price) / old_price) > 0.02:  # 2% move
            print(f"Significant move detected: {symbol} {old_price} -> {price}")


class SentimentProcessor:
    """Process sentiment events."""
    
    async def process(self, event: Event) -> None:
        """Process a sentiment event."""
        data = event.data
        symbol = data["symbol"]
        score = data["score"]
        
        # Detect sentiment shifts
        if abs(score) > 0.5:
            direction = "bullish" if score > 0 else "bearish"
            print(f"Strong {direction} sentiment for {symbol}: {score}")
