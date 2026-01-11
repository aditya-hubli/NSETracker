"""Database operations for notifications and alerts."""
from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4

from supabase import Client

from .models import (
    PriceAlert,
    AlertStatus,
    AlertCondition,
    Notification,
    NotificationType,
)


class NotificationDatabase:
    """Database operations for notifications and alerts."""
    
    def __init__(self, supabase_client: Client):
        self.db = supabase_client
    
    # ==================== Alerts ====================
    
    async def create_alert(self, alert: PriceAlert) -> PriceAlert:
        """Create a new price alert."""
        alert.id = str(uuid4())
        
        data = {
            "id": alert.id,
            "user_id": alert.user_id,
            "symbol": alert.symbol.upper(),
            "condition": alert.condition.value,
            "target_value": alert.target_value,
            "status": alert.status.value,
            "created_at": alert.created_at.isoformat(),
            "message": alert.message,
        }
        
        if alert.expires_at:
            data["expires_at"] = alert.expires_at.isoformat()
        
        try:
            self.db.table("price_alerts").insert(data).execute()
            return alert
        except Exception as e:
            print(f"Error creating alert: {e}")
            raise
    
    async def get_user_alerts(
        self,
        user_id: str,
        status: Optional[AlertStatus] = None
    ) -> list[PriceAlert]:
        """Get all alerts for a user."""
        try:
            query = self.db.table("price_alerts").select("*").eq("user_id", user_id)
            
            if status:
                query = query.eq("status", status.value)
            
            result = query.order("created_at", desc=True).execute()
            
            alerts = []
            for row in result.data:
                alerts.append(PriceAlert(
                    id=row["id"],
                    user_id=row["user_id"],
                    symbol=row["symbol"],
                    condition=AlertCondition(row["condition"]),
                    target_value=row["target_value"],
                    status=AlertStatus(row["status"]),
                    created_at=datetime.fromisoformat(row["created_at"]),
                    triggered_at=datetime.fromisoformat(row["triggered_at"]) if row.get("triggered_at") else None,
                    expires_at=datetime.fromisoformat(row["expires_at"]) if row.get("expires_at") else None,
                    message=row.get("message")
                ))
            
            return alerts
        except Exception as e:
            print(f"Error getting alerts: {e}")
            return []
    
    async def get_active_alerts_for_symbol(self, symbol: str) -> list[PriceAlert]:
        """Get all active alerts for a symbol."""
        try:
            result = (
                self.db.table("price_alerts")
                .select("*")
                .eq("symbol", symbol.upper())
                .eq("status", AlertStatus.ACTIVE.value)
                .execute()
            )
            
            alerts = []
            for row in result.data:
                alerts.append(PriceAlert(
                    id=row["id"],
                    user_id=row["user_id"],
                    symbol=row["symbol"],
                    condition=AlertCondition(row["condition"]),
                    target_value=row["target_value"],
                    status=AlertStatus(row["status"]),
                    created_at=datetime.fromisoformat(row["created_at"]),
                    message=row.get("message")
                ))
            
            return alerts
        except Exception as e:
            print(f"Error getting alerts for symbol: {e}")
            return []
    
    async def trigger_alert(self, alert_id: str, current_price: float) -> None:
        """Mark an alert as triggered."""
        try:
            self.db.table("price_alerts").update({
                "status": AlertStatus.TRIGGERED.value,
                "triggered_at": datetime.utcnow().isoformat(),
                "current_price": current_price
            }).eq("id", alert_id).execute()
        except Exception as e:
            print(f"Error triggering alert: {e}")
    
    async def cancel_alert(self, alert_id: str, user_id: str) -> bool:
        """Cancel an alert."""
        try:
            result = (
                self.db.table("price_alerts")
                .update({"status": AlertStatus.CANCELLED.value})
                .eq("id", alert_id)
                .eq("user_id", user_id)
                .execute()
            )
            return len(result.data) > 0
        except Exception as e:
            print(f"Error cancelling alert: {e}")
            return False
    
    async def expire_old_alerts(self) -> int:
        """Expire alerts past their expiration date."""
        try:
            result = (
                self.db.table("price_alerts")
                .update({"status": AlertStatus.EXPIRED.value})
                .eq("status", AlertStatus.ACTIVE.value)
                .lt("expires_at", datetime.utcnow().isoformat())
                .execute()
            )
            return len(result.data)
        except Exception as e:
            print(f"Error expiring alerts: {e}")
            return 0
    
    # ==================== Notifications ====================
    
    async def create_notification(self, notification: Notification) -> Notification:
        """Create a new notification."""
        notification.id = str(uuid4())
        
        data = {
            "id": notification.id,
            "user_id": notification.user_id,
            "type": notification.type.value,
            "title": notification.title,
            "message": notification.message,
            "symbol": notification.symbol,
            "data": notification.data,
            "read": notification.read,
            "created_at": notification.created_at.isoformat(),
        }
        
        try:
            self.db.table("notifications").insert(data).execute()
            return notification
        except Exception as e:
            print(f"Error creating notification: {e}")
            raise
    
    async def get_user_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50
    ) -> list[Notification]:
        """Get notifications for a user."""
        try:
            query = (
                self.db.table("notifications")
                .select("*")
                .eq("user_id", user_id)
            )
            
            if unread_only:
                query = query.eq("read", False)
            
            result = query.order("created_at", desc=True).limit(limit).execute()
            
            notifications = []
            for row in result.data:
                notifications.append(Notification(
                    id=row["id"],
                    user_id=row["user_id"],
                    type=NotificationType(row["type"]),
                    title=row["title"],
                    message=row["message"],
                    symbol=row.get("symbol"),
                    data=row.get("data"),
                    read=row["read"],
                    created_at=datetime.fromisoformat(row["created_at"])
                ))
            
            return notifications
        except Exception as e:
            print(f"Error getting notifications: {e}")
            return []
    
    async def mark_as_read(self, notification_id: str, user_id: str) -> bool:
        """Mark a notification as read."""
        try:
            result = (
                self.db.table("notifications")
                .update({"read": True})
                .eq("id", notification_id)
                .eq("user_id", user_id)
                .execute()
            )
            return len(result.data) > 0
        except Exception as e:
            print(f"Error marking notification as read: {e}")
            return False
    
    async def mark_all_as_read(self, user_id: str) -> int:
        """Mark all notifications as read for a user."""
        try:
            result = (
                self.db.table("notifications")
                .update({"read": True})
                .eq("user_id", user_id)
                .eq("read", False)
                .execute()
            )
            return len(result.data)
        except Exception as e:
            print(f"Error marking all notifications as read: {e}")
            return 0
    
    async def get_unread_count(self, user_id: str) -> int:
        """Get count of unread notifications."""
        try:
            result = (
                self.db.table("notifications")
                .select("id", count="exact")
                .eq("user_id", user_id)
                .eq("read", False)
                .execute()
            )
            return result.count or 0
        except Exception as e:
            print(f"Error getting unread count: {e}")
            return 0
