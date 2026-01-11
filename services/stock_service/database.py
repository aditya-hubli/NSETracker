"""Watchlist database operations."""

from datetime import datetime
from typing import Any

import httpx

from shared.config import get_settings
from shared.logging_config import setup_logging

settings = get_settings()
logger = setup_logging(service_name="watchlist-database")


class WatchlistRepository:
    """Repository for watchlist database operations using Supabase REST API."""

    def __init__(self) -> None:
        """Initialize the repository."""
        self.base_url = f"{settings.supabase_url}/rest/v1"
        self.headers = {
            "apikey": settings.supabase_anon_key,
            "Authorization": f"Bearer {settings.supabase_anon_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }

    async def create_watchlist(self, data: dict[str, Any]) -> dict[str, Any] | None:
        """Create a new watchlist."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/watchlists",
                    headers=self.headers,
                    json=data,
                )
                response.raise_for_status()
                result = response.json()
                return result[0] if result else None
        except Exception as e:
            logger.error(f"Failed to create watchlist: {e}")
            return None

    async def get_watchlist(self, watchlist_id: str) -> dict[str, Any] | None:
        """Get a watchlist by ID."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/watchlists",
                    headers=self.headers,
                    params={"id": f"eq.{watchlist_id}", "select": "*"},
                )
                response.raise_for_status()
                result = response.json()
                return result[0] if result else None
        except Exception as e:
            logger.error(f"Failed to get watchlist: {e}")
            return None

    async def get_user_watchlists(self, user_id: str) -> list[dict[str, Any]]:
        """Get all watchlists for a user."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/watchlists",
                    headers=self.headers,
                    params={
                        "user_id": f"eq.{user_id}",
                        "select": "*",
                        "order": "created_at.desc",
                    },
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to get user watchlists: {e}")
            return []

    async def update_watchlist(
        self, watchlist_id: str, data: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Update a watchlist."""
        try:
            data["updated_at"] = datetime.utcnow().isoformat()
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.base_url}/watchlists",
                    headers=self.headers,
                    params={"id": f"eq.{watchlist_id}"},
                    json=data,
                )
                response.raise_for_status()
                result = response.json()
                return result[0] if result else None
        except Exception as e:
            logger.error(f"Failed to update watchlist: {e}")
            return None

    async def delete_watchlist(self, watchlist_id: str) -> bool:
        """Delete a watchlist."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.base_url}/watchlists",
                    headers=self.headers,
                    params={"id": f"eq.{watchlist_id}"},
                )
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Failed to delete watchlist: {e}")
            return False

    async def add_symbol_to_watchlist(
        self, watchlist_id: str, symbol: str
    ) -> dict[str, Any] | None:
        """Add a symbol to a watchlist."""
        watchlist = await self.get_watchlist(watchlist_id)
        if not watchlist:
            return None
        
        symbols = watchlist.get("symbols", [])
        if symbol.upper() not in symbols:
            symbols.append(symbol.upper())
            return await self.update_watchlist(watchlist_id, {"symbols": symbols})
        return watchlist

    async def remove_symbol_from_watchlist(
        self, watchlist_id: str, symbol: str
    ) -> dict[str, Any] | None:
        """Remove a symbol from a watchlist."""
        watchlist = await self.get_watchlist(watchlist_id)
        if not watchlist:
            return None
        
        symbols = watchlist.get("symbols", [])
        symbol_upper = symbol.upper()
        if symbol_upper in symbols:
            symbols.remove(symbol_upper)
            return await self.update_watchlist(watchlist_id, {"symbols": symbols})
        return watchlist
