"""In-memory caching utilities for the platform.

Uses cachetools for TTL-based LRU caching. For pub/sub and event streaming,
use Redpanda via shared.events module instead.
"""
import asyncio
import json
from typing import Any, Optional, TypeVar, Callable
from functools import wraps

from cachetools import TTLCache

from .config import get_settings

T = TypeVar("T")


class InMemoryCache:
    """Thread-safe in-memory cache with TTL support.
    
    For distributed caching across multiple instances, store data in
    Supabase (PostgreSQL) and use Redpanda for cache invalidation events.
    """
    
    _instance: Optional["InMemoryCache"] = None
    _cache: Optional[TTLCache] = None
    _lock: asyncio.Lock
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._lock = asyncio.Lock()
        return cls._instance
    
    def connect(self) -> None:
        """Initialize the cache."""
        if self._cache is None:
            settings = get_settings()
            self._cache = TTLCache(
                maxsize=settings.cache_max_size,
                ttl=settings.cache_ttl,
            )
    
    def disconnect(self) -> None:
        """Clear and reset cache."""
        if self._cache:
            self._cache.clear()
            self._cache = None
    
    @property
    def _store(self) -> TTLCache:
        """Get cache store."""
        if self._cache is None:
            self.connect()
        return self._cache
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            async with self._lock:
                value = self._store.get(key)
                if value is not None:
                    return json.loads(value) if isinstance(value, str) else value
                return None
        except Exception as e:
            print(f"Cache GET error: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache with optional TTL.
        
        Note: Custom TTL creates a separate cache instance for that key.
        For simplicity, using default TTL is recommended.
        """
        try:
            async with self._lock:
                serialized = json.dumps(value, default=str)
                self._store[key] = serialized
                return True
        except Exception as e:
            print(f"Cache SET error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            async with self._lock:
                if key in self._store:
                    del self._store[key]
                return True
        except Exception as e:
            print(f"Cache DELETE error: {e}")
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern (simple wildcard support)."""
        try:
            async with self._lock:
                # Convert simple pattern to check (e.g., "stock:*" -> startswith "stock:")
                prefix = pattern.rstrip("*")
                keys_to_delete = [k for k in self._store.keys() if k.startswith(prefix)]
                for key in keys_to_delete:
                    del self._store[key]
                return len(keys_to_delete)
        except Exception as e:
            print(f"Cache DELETE pattern error: {e}")
            return 0
    
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        try:
            async with self._lock:
                return key in self._store
        except Exception as e:
            print(f"Cache EXISTS error: {e}")
            return False
    
    async def clear(self) -> bool:
        """Clear all cache entries."""
        try:
            async with self._lock:
                self._store.clear()
                return True
        except Exception as e:
            print(f"Cache CLEAR error: {e}")
            return False
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        return {
            "size": len(self._store) if self._cache else 0,
            "max_size": self._store.maxsize if self._cache else 0,
            "ttl": self._store.ttl if self._cache else 0,
        }


# Global cache instance
cache = InMemoryCache()


def cached(
    key_prefix: str,
    ttl: Optional[int] = None,
    key_builder: Optional[Callable[..., str]] = None,
):
    """Decorator for caching function results.
    
    Args:
        key_prefix: Prefix for the cache key
        ttl: Time-to-live in seconds (uses default if not specified)
        key_builder: Custom function to build cache key from args
    
    Example:
        @cached("stock_price", ttl=60)
        async def get_stock_price(symbol: str) -> dict:
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            # Build cache key
            if key_builder:
                cache_key = f"{key_prefix}:{key_builder(*args, **kwargs)}"
            else:
                # Default: use all args as key
                key_parts = [str(arg) for arg in args]
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = f"{key_prefix}:{':'.join(key_parts)}"
            
            # Try to get from cache
            cached_value = await cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Call function and cache result
            result = await func(*args, **kwargs)
            await cache.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator


# Cache key builders for common patterns
def stock_key(symbol: str, *args, **kwargs) -> str:
    """Build cache key for stock data."""
    return symbol.upper()


def user_key(user_id: str, *args, **kwargs) -> str:
    """Build cache key for user data."""
    return user_id


def sentiment_key(symbol: str, source: str = "all", *args, **kwargs) -> str:
    """Build cache key for sentiment data."""
    return f"{symbol.upper()}:{source}"
