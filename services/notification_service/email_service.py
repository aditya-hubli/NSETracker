"""Email notification service - supports SMTP (primary) or Resend API (fallback)."""

import smtplib
import ssl
import httpx
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime

from shared.config import get_settings


class EmailService:
    """Service for sending email notifications via SMTP (primary) or Resend API."""

    def __init__(self):
        self.settings = get_settings()
        self._smtp_connection: Optional[smtplib.SMTP] = None

    @property
    def is_configured(self) -> bool:
        """Check if email is properly configured."""
        if not self.settings.email_enabled:
            return False
        
        # Check SMTP first (preferred - works with any email)
        if (self.settings.smtp_username 
            and self.settings.smtp_password 
            and self.settings.smtp_from_email):
            return True
        
        # Fall back to Resend API
        return bool(self.settings.resend_api_key)

    @property
    def _use_smtp(self) -> bool:
        """Check if we should use SMTP (preferred over Resend)."""
        return bool(
            self.settings.smtp_username
            and self.settings.smtp_password
            and self.settings.smtp_from_email
        )

    def _send_via_resend(
        self,
        to_email: str,
        subject: str,
        html_body: str,
    ) -> bool:
        """Send email via Resend API."""
        try:
            response = httpx.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {self.settings.resend_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "from": f"{self.settings.smtp_from_name} <onboarding@resend.dev>",
                    "to": [to_email],
                    "subject": subject,
                    "html": html_body,
                },
                timeout=10.0,
            )
            
            if response.status_code in (200, 202):
                print(f"Email sent successfully via Resend to {to_email}")
                return True
            else:
                print(f"Resend error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Error sending via Resend: {e}")
            return False

    def _get_smtp_connection(self) -> smtplib.SMTP:
        """Get or create SMTP connection."""
        if self._smtp_connection is None:
            context = ssl.create_default_context()
            self._smtp_connection = smtplib.SMTP(
                self.settings.smtp_host, self.settings.smtp_port
            )
            self._smtp_connection.starttls(context=context)
            self._smtp_connection.login(
                self.settings.smtp_username, self.settings.smtp_password
            )
        return self._smtp_connection

    def _send_via_smtp(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
    ) -> bool:
        """Send email via SMTP."""
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.settings.smtp_from_name} <{self.settings.smtp_from_email}>"
            message["To"] = to_email

            if text_body:
                message.attach(MIMEText(text_body, "plain"))
            message.attach(MIMEText(html_body, "html"))

            connection = self._get_smtp_connection()
            connection.sendmail(
                self.settings.smtp_from_email, to_email, message.as_string()
            )
            
            print(f"Email sent successfully via SMTP to {to_email}")
            return True

        except smtplib.SMTPException as e:
            print(f"SMTP error: {e}")
            self.close()
            return False
        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    def close(self):
        """Close SMTP connection."""
        if self._smtp_connection:
            try:
                self._smtp_connection.quit()
            except Exception:
                pass
            self._smtp_connection = None

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
    ) -> bool:
        """Send an email using configured provider (SMTP preferred, Resend fallback)."""
        if not self.is_configured:
            print("Email not configured - skipping send")
            return False

        # Prefer SMTP (works with any email address)
        if self._use_smtp:
            return self._send_via_smtp(to_email, subject, html_body, text_body)
        else:
            # Fallback to Resend API
            return self._send_via_resend(to_email, subject, html_body)

    def send_price_alert(
        self,
        to_email: str,
        symbol: str,
        condition: str,
        target_price: float,
        current_price: float,
        change_percent: float,
    ) -> bool:
        """Send a price alert email."""
        display_symbol = symbol.replace(".NS", "").replace(".BO", "")
        exchange = "NSE" if ".NS" in symbol else "BSE" if ".BO" in symbol else ""
        
        is_positive = change_percent >= 0
        change_color = "#10b981" if is_positive else "#ef4444"
        change_icon = "▲" if is_positive else "▼"
        
        subject = f"Price Alert: {display_symbol} {condition} ₹{target_price:,.2f}"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f9fafb; margin: 0; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 30px; text-align: center;">
                    <h1 style="color: white; margin: 0; font-size: 24px;">Price Alert Triggered</h1>
                </div>
                
                <!-- Content -->
                <div style="padding: 30px;">
                    <!-- Stock Info -->
                    <div style="background: #f3f4f6; border-radius: 12px; padding: 20px; margin-bottom: 20px;">
                        <div style="margin-bottom: 15px;">
                            <h2 style="margin: 0; color: #111827; font-size: 22px;">{display_symbol}</h2>
                            <span style="color: #6b7280; font-size: 14px;">{exchange}</span>
                        </div>
                        
                        <div style="font-size: 32px; font-weight: bold; color: #111827; margin-bottom: 10px;">
                            ₹{current_price:,.2f}
                        </div>
                        
                        <div style="display: inline-block; background-color: {change_color}20; color: {change_color}; padding: 6px 12px; border-radius: 8px; font-weight: 600;">
                            {change_icon} {'+' if is_positive else ''}{change_percent:.2f}%
                        </div>
                    </div>
                    
                    <!-- Alert Details -->
                    <div style="border: 1px solid #e5e7eb; border-radius: 12px; padding: 20px;">
                        <h3 style="margin: 0 0 15px 0; color: #374151; font-size: 16px;">Alert Details</h3>
                        
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="padding: 10px 0; color: #6b7280; border-bottom: 1px solid #f3f4f6;">Condition</td>
                                <td style="padding: 10px 0; color: #111827; font-weight: 600; text-align: right; border-bottom: 1px solid #f3f4f6;">{condition.replace('_', ' ').title()}</td>
                            </tr>
                            <tr>
                                <td style="padding: 10px 0; color: #6b7280; border-bottom: 1px solid #f3f4f6;">Target Price</td>
                                <td style="padding: 10px 0; color: #111827; font-weight: 600; text-align: right; border-bottom: 1px solid #f3f4f6;">₹{target_price:,.2f}</td>
                            </tr>
                            <tr>
                                <td style="padding: 10px 0; color: #6b7280;">Triggered At</td>
                                <td style="padding: 10px 0; color: #111827; font-weight: 600; text-align: right;">{datetime.now().strftime('%d %b %Y, %I:%M %p IST')}</td>
                            </tr>
                        </table>
                    </div>
                </div>
                
                <!-- Footer -->
                <div style="background: #f9fafb; padding: 20px; text-align: center; border-top: 1px solid #e5e7eb;">
                    <p style="color: #9ca3af; font-size: 12px; margin: 0;">
                        You received this because you set up a price alert on Stock Platform.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(to_email, subject, html_body)

    def send_test_email(self, to_email: str) -> bool:
        """Send a test email to verify configuration."""
        subject = "Stock Platform - Email Test Successful"
        
        html_body = """
        <!DOCTYPE html>
        <html>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f9fafb; margin: 0; padding: 20px;">
            <div style="max-width: 500px; margin: 0 auto; background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 30px; text-align: center;">
                    <h1 style="color: white; margin: 0; font-size: 24px;">Email Test Successful!</h1>
                </div>
                <div style="padding: 30px; text-align: center;">
                    <p style="color: #374151; font-size: 16px; margin: 0;">
                        Your email notifications are configured correctly.<br>
                        You'll receive alerts when your price targets are hit.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(to_email, subject, html_body)

    def send_market_open_alert(self, to_email: str) -> bool:
        """Send market open notification."""
        subject = "🔔 NSE/BSE Markets Are Now Open"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f9fafb; margin: 0; padding: 20px;">
            <div style="max-width: 500px; margin: 0 auto; background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 30px; text-align: center;">
                    <h1 style="color: white; margin: 0; font-size: 24px;">🔔 Markets Open!</h1>
                </div>
                <div style="padding: 30px; text-align: center;">
                    <div style="font-size: 48px; margin-bottom: 20px;">📈</div>
                    <h2 style="color: #111827; margin: 0 0 10px 0;">Trading Session Started</h2>
                    <p style="color: #6b7280; font-size: 16px; margin: 0 0 20px 0;">
                        NSE & BSE markets are now open for trading.<br>
                        Session: 9:15 AM - 3:30 PM IST
                    </p>
                    <p style="color: #9ca3af; font-size: 14px; margin: 0;">
                        {datetime.now().strftime('%A, %d %B %Y')}
                    </p>
                </div>
                <div style="background: #f9fafb; padding: 20px; text-align: center; border-top: 1px solid #e5e7eb;">
                    <p style="color: #9ca3af; font-size: 12px; margin: 0;">
                        Manage your alerts in Settings → Notifications
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(to_email, subject, html_body)

    def send_market_close_alert(self, to_email: str, market_summary: dict = None) -> bool:
        """Send market close notification with optional summary."""
        subject = "🔕 NSE/BSE Markets Are Now Closed"
        
        summary_html = ""
        if market_summary:
            nifty = market_summary.get('nifty', {})
            sensex = market_summary.get('sensex', {})
            nifty_change = nifty.get('change_percent', 0)
            sensex_change = sensex.get('change_percent', 0)
            nifty_color = "#10b981" if nifty_change >= 0 else "#ef4444"
            sensex_color = "#10b981" if sensex_change >= 0 else "#ef4444"
            
            summary_html = f"""
            <div style="background: #f3f4f6; border-radius: 12px; padding: 20px; margin: 20px 0;">
                <h3 style="margin: 0 0 15px 0; color: #374151; font-size: 16px; text-align: center;">Today's Summary</h3>
                <div style="display: flex; justify-content: space-around; text-align: center;">
                    <div>
                        <div style="color: #6b7280; font-size: 12px;">NIFTY 50</div>
                        <div style="color: #111827; font-size: 18px; font-weight: bold;">₹{nifty.get('price', 0):,.2f}</div>
                        <div style="color: {nifty_color}; font-size: 14px;">{'+' if nifty_change >= 0 else ''}{nifty_change:.2f}%</div>
                    </div>
                    <div>
                        <div style="color: #6b7280; font-size: 12px;">SENSEX</div>
                        <div style="color: #111827; font-size: 18px; font-weight: bold;">₹{sensex.get('price', 0):,.2f}</div>
                        <div style="color: {sensex_color}; font-size: 14px;">{'+' if sensex_change >= 0 else ''}{sensex_change:.2f}%</div>
                    </div>
                </div>
            </div>
            """
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f9fafb; margin: 0; padding: 20px;">
            <div style="max-width: 500px; margin: 0 auto; background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%); padding: 30px; text-align: center;">
                    <h1 style="color: white; margin: 0; font-size: 24px;">🔕 Markets Closed</h1>
                </div>
                <div style="padding: 30px; text-align: center;">
                    <div style="font-size: 48px; margin-bottom: 20px;">📊</div>
                    <h2 style="color: #111827; margin: 0 0 10px 0;">Trading Session Ended</h2>
                    <p style="color: #6b7280; font-size: 16px; margin: 0;">
                        NSE & BSE markets are now closed.<br>
                        Next session: Tomorrow 9:15 AM IST
                    </p>
                    {summary_html}
                    <p style="color: #9ca3af; font-size: 14px; margin: 20px 0 0 0;">
                        {datetime.now().strftime('%A, %d %B %Y at %I:%M %p IST')}
                    </p>
                </div>
                <div style="background: #f9fafb; padding: 20px; text-align: center; border-top: 1px solid #e5e7eb;">
                    <p style="color: #9ca3af; font-size: 12px; margin: 0;">
                        Manage your alerts in Settings → Notifications
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(to_email, subject, html_body)

    def send_daily_digest(self, to_email: str, watchlist_stocks: list, user_name: str = "Investor") -> bool:
        """Send daily digest with watchlist summary."""
        subject = f"📊 Your Daily Stock Digest - {datetime.now().strftime('%d %b %Y')}"
        
        # Build stock rows
        stock_rows = ""
        for stock in watchlist_stocks[:10]:  # Limit to 10 stocks
            change = stock.get('change_percent', 0)
            change_color = "#10b981" if change >= 0 else "#ef4444"
            change_icon = "▲" if change >= 0 else "▼"
            
            stock_rows += f"""
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #f3f4f6;">
                    <div style="font-weight: 600; color: #111827;">{stock.get('symbol', 'N/A')}</div>
                    <div style="font-size: 12px; color: #6b7280;">{stock.get('name', '')[:25]}</div>
                </td>
                <td style="padding: 12px; border-bottom: 1px solid #f3f4f6; text-align: right;">
                    <div style="font-weight: 600; color: #111827;">₹{stock.get('price', 0):,.2f}</div>
                </td>
                <td style="padding: 12px; border-bottom: 1px solid #f3f4f6; text-align: right;">
                    <span style="color: {change_color}; font-weight: 600;">
                        {change_icon} {'+' if change >= 0 else ''}{change:.2f}%
                    </span>
                </td>
            </tr>
            """
        
        if not stock_rows:
            stock_rows = """
            <tr>
                <td colspan="3" style="padding: 30px; text-align: center; color: #6b7280;">
                    No stocks in your watchlist yet.<br>
                    Add stocks to get daily updates!
                </td>
            </tr>
            """
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f9fafb; margin: 0; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); padding: 30px; text-align: center;">
                    <h1 style="color: white; margin: 0; font-size: 24px;">📊 Daily Stock Digest</h1>
                    <p style="color: rgba(255,255,255,0.8); margin: 10px 0 0 0;">{datetime.now().strftime('%A, %d %B %Y')}</p>
                </div>
                
                <div style="padding: 30px;">
                    <p style="color: #374151; font-size: 16px; margin: 0 0 20px 0;">
                        Good morning, {user_name}! Here's your watchlist summary:
                    </p>
                    
                    <table style="width: 100%; border-collapse: collapse; background: #f9fafb; border-radius: 12px; overflow: hidden;">
                        <thead>
                            <tr style="background: #f3f4f6;">
                                <th style="padding: 12px; text-align: left; color: #6b7280; font-weight: 600; font-size: 12px;">STOCK</th>
                                <th style="padding: 12px; text-align: right; color: #6b7280; font-weight: 600; font-size: 12px;">PRICE</th>
                                <th style="padding: 12px; text-align: right; color: #6b7280; font-weight: 600; font-size: 12px;">CHANGE</th>
                            </tr>
                        </thead>
                        <tbody>
                            {stock_rows}
                        </tbody>
                    </table>
                </div>
                
                <div style="background: #f9fafb; padding: 20px; text-align: center; border-top: 1px solid #e5e7eb;">
                    <p style="color: #9ca3af; font-size: 12px; margin: 0;">
                        Manage your digest preferences in Settings → Notifications
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(to_email, subject, html_body)


# Singleton instance
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """Get email service singleton."""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
