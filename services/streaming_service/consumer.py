"""Stock price consumer - consumes from Kafka (Aiven/Redpanda) and broadcasts via WebSocket."""

import asyncio
import ssl
from typing import Optional, Callable, Any
import json

from aiokafka import AIOKafkaConsumer

from shared.config import get_settings
from shared.events import get_kafka_ssl_context

TOPIC_STOCK_PRICES = "stock-prices"


class StockPriceConsumer:
    """Consumes stock prices from Kafka (Aiven/Redpanda) and broadcasts to WebSocket clients."""
    
    def __init__(self, on_message: Optional[Callable[[dict], Any]] = None):
        self.settings = get_settings()
        self._consumer: Optional[AIOKafkaConsumer] = None
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._on_message = on_message
        self._handlers: list[Callable[[dict], Any]] = []
    
    def add_handler(self, handler: Callable[[dict], Any]) -> None:
        """Add a message handler."""
        self._handlers.append(handler)
    
    def remove_handler(self, handler: Callable[[dict], Any]) -> None:
        """Remove a message handler."""
        if handler in self._handlers:
            self._handlers.remove(handler)
    
    async def start(self) -> bool:
        """Start the consumer."""
        try:
            # Build Kafka connection config
            kafka_config = {
                "bootstrap_servers": self.settings.kafka_brokers,
                "group_id": f"websocket-broadcaster-{id(self)}",
                "value_deserializer": lambda m: json.loads(m.decode('utf-8')),
                "auto_offset_reset": 'latest',
                "enable_auto_commit": True,
                "auto_commit_interval_ms": 5000,
                "session_timeout_ms": 30000,
                "heartbeat_interval_ms": 10000,
                "max_poll_interval_ms": 300000,
            }
            
            # Add security config for Aiven/cloud Kafka
            if self.settings.kafka_security_protocol != "PLAINTEXT":
                kafka_config["security_protocol"] = self.settings.kafka_security_protocol
                
                # SSL context
                ssl_context = get_kafka_ssl_context(self.settings)
                if ssl_context:
                    kafka_config["ssl_context"] = ssl_context
                
                # SASL authentication
                if self.settings.kafka_security_protocol in ("SASL_SSL", "SASL_PLAINTEXT"):
                    kafka_config["sasl_mechanism"] = self.settings.kafka_sasl_mechanism
                    kafka_config["sasl_plain_username"] = self.settings.kafka_sasl_username
                    kafka_config["sasl_plain_password"] = self.settings.kafka_sasl_password
            
            self._consumer = AIOKafkaConsumer(TOPIC_STOCK_PRICES, **kafka_config)
            await self._consumer.start()
            self._running = True
            print(f"Stock price consumer connected to {self.settings.kafka_brokers}")
            
            # Start consume loop
            self._task = asyncio.create_task(self._consume_loop())
            return True
            
        except Exception as e:
            print(f"Failed to start consumer: {e}")
            return False
    
    async def stop(self) -> None:
        """Stop the consumer."""
        self._running = False
        
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        if self._consumer:
            await self._consumer.stop()
            self._consumer = None
            print("Stock price consumer stopped")
    
    async def _consume_loop(self) -> None:
        """Main consume loop."""
        if not self._consumer:
            return
        
        print("Stock price consumer started listening...")
        
        while self._running:
            try:
                async for msg in self._consumer:
                    if not self._running:
                        break
                    
                    try:
                        data = msg.value
                        
                        # Call registered handlers
                        for handler in self._handlers:
                            try:
                                if asyncio.iscoroutinefunction(handler):
                                    await handler(data)
                                else:
                                    handler(data)
                            except Exception as e:
                                print(f"Handler error: {e}")
                        
                        # Call legacy on_message callback
                        if self._on_message:
                            if asyncio.iscoroutinefunction(self._on_message):
                                await self._on_message(data)
                            else:
                                self._on_message(data)
                                
                    except Exception as e:
                        print(f"Error processing message: {e}")
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                # Log error and continue - don't crash
                print(f"Consumer loop error (will retry): {e}")
                await asyncio.sleep(2)  # Wait before retrying


# Global consumer instance
_consumer: Optional[StockPriceConsumer] = None


async def start_consumer(on_message: Optional[Callable[[dict], Any]] = None) -> bool:
    """Start the global stock price consumer."""
    global _consumer
    
    if _consumer is not None:
        return True
    
    _consumer = StockPriceConsumer(on_message)
    return await _consumer.start()


async def stop_consumer() -> None:
    """Stop the global stock price consumer."""
    global _consumer
    
    if _consumer:
        await _consumer.stop()
        _consumer = None


def get_consumer() -> Optional[StockPriceConsumer]:
    """Get the global consumer instance."""
    return _consumer
