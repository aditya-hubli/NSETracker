"""Email notification service - supports Resend API or SMTP."""

import smtplib
import ssl
import httpx
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime

from shared.config import get_settings


class EmailService:
    """Service for sending email notifications via Resend or SMTP."""

    def __init__(self):
        self.settings = get_settings()
        self._smtp_connection: Optional[smtplib.SMTP] = None

    @property
    def is_configured(self) -> bool:
        """Check if email is properly configured."""
        if not self.settings.email_enabled:
            return False
        
        # Check Resend first (preferred)
        if self.settings.resend_api_key:
            return True
        
        # Fall back to SMTP
        return bool(
            self.settings.smtp_username
            and self.settings.smtp_password
            and self.settings.smtp_from_email
        )

    @property
    def _use_resend(self) -> bool:
        """Check if we should use Resend API."""
        return bool(self.settings.resend_api_key)

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
            
            if response.status_code == 200:
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
        """Send an email using configured provider (Resend or SMTP)."""
        if not self.is_configured:
            print("Email not configured - skipping send")
            return False

        if self._use_resend:
            return self._send_via_resend(to_email, subject, html_body)
        else:
            return self._send_via_smtp(to_email, subject, html_body, text_body)

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


# Singleton instance
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """Get email service singleton."""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
