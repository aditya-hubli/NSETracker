"""Alert checker service - monitors prices and triggers alerts."""
import asyncio
from datetime import datetime
from typing import Optional

import yfinance as yf

from .models import (
    PriceAlert,
    AlertCondition,
    AlertStatus,
    Notification,
    NotificationType,
    WebSocketMessage,
)
from .database import NotificationDatabase
from .websocket_manager import manager
from .email_service import get_email_service


class AlertChecker:
    """Check and trigger price alerts."""
    
    def __init__(self, db: NotificationDatabase):
        self.db = db
        self._running = False
        self._task: Optional[asyncio.Task] = None
    
    async def start(self, check_interval: int = 30):
        """Start the alert checker background task."""
        self._running = True
        self._task = asyncio.create_task(self._check_loop(check_interval))
    
    async def stop(self):
        """Stop the alert checker."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
    
    async def _check_loop(self, interval: int):
        """Main loop for checking alerts."""
        while self._running:
            try:
                await self._check_all_alerts()
                await self.db.expire_old_alerts()
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in alert check loop: {e}")
                await asyncio.sleep(interval)
    
    async def _check_all_alerts(self):
        """Check all active alerts against current prices."""
        # Get all unique symbols with active alerts
        # This is a simplified version - in production, batch this properly
        try:
            result = self.db.db.table("price_alerts").select("symbol").eq(
                "status", AlertStatus.ACTIVE.value
            ).execute()
            
            symbols = list(set(row["symbol"] for row in result.data))
            
            if not symbols:
                return
            
            # Fetch current prices
            prices = await self._fetch_prices(symbols)
            
            # Check each symbol's alerts
            for symbol, price in prices.items():
                if price is None:
                    continue
                
                alerts = await self.db.get_active_alerts_for_symbol(symbol)
                
                for alert in alerts:
                    triggered = self._check_alert_condition(alert, price)
                    
                    if triggered:
                        await self._trigger_alert(alert, price)
        
        except Exception as e:
            print(f"Error checking alerts: {e}")
    
    def _check_alert_condition(self, alert: PriceAlert, current_price: float) -> bool:
        """Check if alert condition is met."""
        if alert.condition == AlertCondition.ABOVE:
            return current_price >= alert.target_value
        
        elif alert.condition == AlertCondition.BELOW:
            return current_price <= alert.target_value
        
        elif alert.condition == AlertCondition.PERCENT_UP:
            # Need reference price (stored when alert created)
            if alert.current_price:
                change_percent = ((current_price - alert.current_price) / alert.current_price) * 100
                return change_percent >= alert.target_value
            return False
        
        elif alert.condition == AlertCondition.PERCENT_DOWN:
            if alert.current_price:
                change_percent = ((alert.current_price - current_price) / alert.current_price) * 100
                return change_percent >= alert.target_value
            return False
        
        return False
    
    async def _trigger_alert(self, alert: PriceAlert, current_price: float):
        """Trigger an alert and notify the user."""
        # Update alert status
        await self.db.trigger_alert(alert.id, current_price)
        
        # Create notification
        condition_text = {
            AlertCondition.ABOVE: f"risen above ${alert.target_value:.2f}",
            AlertCondition.BELOW: f"fallen below ${alert.target_value:.2f}",
            AlertCondition.PERCENT_UP: f"increased by {alert.target_value}%",
            AlertCondition.PERCENT_DOWN: f"decreased by {alert.target_value}%",
        }
        
        notification = Notification(
            user_id=alert.user_id,
            type=NotificationType.PRICE_ALERT,
            title=f"Price Alert: {alert.symbol}",
            message=alert.message or f"{alert.symbol} has {condition_text[alert.condition]}. Current price: ${current_price:.2f}",
            symbol=alert.symbol,
            data={
                "alert_id": alert.id,
                "condition": alert.condition.value,
                "target_value": alert.target_value,
                "current_price": current_price,
            }
        )
        
        await self.db.create_notification(notification)
        
        # Send WebSocket notification
        await manager.send_personal_message(
            alert.user_id,
            WebSocketMessage(
                event="alert_triggered",
                data=notification.model_dump(mode="json")
            )
        )
        
        # Send email notification
        await self._send_email_notification(alert, current_price)
        
        print(f"Alert triggered for {alert.user_id}: {alert.symbol} at ${current_price:.2f}")
    
    async def _send_email_notification(self, alert: PriceAlert, current_price: float):
        """Send email notification for triggered alert."""
        try:
            email_service = get_email_service()
            
            if not email_service.is_configured:
                print("Email service not configured, skipping email notification")
                return
            
            # Get user email from database
            result = self.db.db.table("users").select("email").eq("id", alert.user_id).execute()
            
            if not result.data:
                print(f"Could not find email for user {alert.user_id}")
                return
            
            user_email = result.data[0]["email"]
            
            # Send the alert email
            success = email_service.send_price_alert(
                to_email=user_email,
                symbol=alert.symbol,
                condition=alert.condition.value,
                target_value=alert.target_value,
                current_price=current_price,
                message=alert.message
            )
            
            if success:
                print(f"Email notification sent to {user_email} for {alert.symbol}")
            else:
                print(f"Failed to send email to {user_email}")
                
        except Exception as e:
            print(f"Error sending email notification: {e}")
    
    async def _fetch_prices(self, symbols: list[str]) -> dict[str, Optional[float]]:
        """Fetch current prices for multiple symbols."""
        prices = {}
        
        try:
            tickers = yf.Tickers(" ".join(symbols))
            
            for symbol in symbols:
                try:
                    ticker = tickers.tickers.get(symbol)
                    if ticker:
                        prices[symbol] = ticker.fast_info.last_price
                    else:
                        prices[symbol] = None
                except Exception:
                    prices[symbol] = None
        
        except Exception as e:
            print(f"Error fetching prices: {e}")
        
        return prices
