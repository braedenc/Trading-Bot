"""
Alert system for trading bot notifications.
Supports Slack webhook and email notifications.
"""

import os
import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import json

# Optional imports with fallback
try:
    import httpx
except ImportError:
    httpx = None

try:
    import aiosmtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
except ImportError:
    aiosmtplib = None
    MIMEText = None
    MIMEMultipart = None

logger = logging.getLogger(__name__)


class AlertConfig:
    """Configuration for alert system."""
    
    def __init__(self):
        self.slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.email_from = os.getenv('EMAIL_FROM')
        self.email_to = os.getenv('EMAIL_TO')
        
    @property
    def slack_enabled(self) -> bool:
        """Check if Slack notifications are enabled."""
        return bool(self.slack_webhook_url and httpx)
    
    @property
    def email_enabled(self) -> bool:
        """Check if email notifications are enabled."""
        return bool(
            self.smtp_username and 
            self.smtp_password and 
            self.email_from and 
            self.email_to and
            aiosmtplib and 
            MIMEText and 
            MIMEMultipart
        )


config = AlertConfig()


async def send_slack(message: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
    """
    Send message to Slack via webhook.
    
    Args:
        message: Message text to send
        metadata: Optional metadata to include in the message
        
    Returns:
        bool: True if sent successfully, False otherwise
    """
    if not config.slack_enabled:
        if config.slack_webhook_url:
            logger.warning("Slack webhook URL provided but httpx not available")
        else:
            logger.debug("Slack webhook URL not configured, skipping Slack notification")
        return False
    
    try:
        payload = {
            "text": message,
            "username": "TradingBot",
            "icon_emoji": ":robot_face:"
        }
        
        # Add metadata as attachment if provided
        if metadata:
            payload["attachments"] = [{
                "color": "good",
                "fields": [
                    {"title": str(key), "value": str(value), "short": True}
                    for key, value in metadata.items()
                ]
            }]
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                config.slack_webhook_url,
                json=payload,
                timeout=10.0
            )
            response.raise_for_status()
            
        logger.info("Slack notification sent successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send Slack notification: {e}")
        return False


async def send_email(message: str, subject: str = "Trading Bot Alert", metadata: Optional[Dict[str, Any]] = None) -> bool:
    """
    Send email notification via SMTP.
    
    Args:
        message: Message text to send
        subject: Email subject line
        metadata: Optional metadata to include in the email
        
    Returns:
        bool: True if sent successfully, False otherwise
    """
    if not config.email_enabled:
        logger.debug("Email not configured, skipping email notification")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = config.email_from or ""
        msg['To'] = config.email_to or ""
        msg['Subject'] = subject
        
        # Create email body
        body = f"{message}\n\n"
        if metadata:
            body += "Additional Information:\n"
            for key, value in metadata.items():
                body += f"  {key}: {value}\n"
        body += f"\nSent at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        async with aiosmtplib.SMTP(hostname=config.smtp_server, port=config.smtp_port) as server:
            await server.starttls()
            await server.login(config.smtp_username, config.smtp_password)
            await server.send_message(msg)
            
        logger.info("Email notification sent successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email notification: {e}")
        return False


async def send_alert(message: str, subject: str = "Trading Bot Alert", metadata: Optional[Dict[str, Any]] = None) -> Dict[str, bool]:
    """
    Send alert via both Slack and email.
    
    Args:
        message: Message text to send
        subject: Subject line (used for email)
        metadata: Optional metadata to include
        
    Returns:
        Dict with success status for each channel
    """
    results = {}
    
    # Send notifications in parallel
    tasks = []
    
    if config.slack_enabled:
        tasks.append(('slack', send_slack(message, metadata)))
    
    if config.email_enabled:
        tasks.append(('email', send_email(message, subject, metadata)))
    
    if not tasks:
        logger.warning("No notification channels configured")
        return {'slack': False, 'email': False}
    
    # Execute all tasks
    for channel, task in tasks:
        try:
            results[channel] = await task
        except Exception as e:
            logger.error(f"Error sending {channel} notification: {e}")
            results[channel] = False
    
    return results


def format_fill_summary(fill: Dict[str, Any]) -> str:
    """
    Format fill information for notifications.
    
    Args:
        fill: Fill information dictionary
        
    Returns:
        Formatted message string
    """
    symbol = fill.get('symbol', 'UNKNOWN')
    side = fill.get('side', 'unknown')
    quantity = fill.get('quantity', 0)
    price = fill.get('price', 0)
    timestamp = fill.get('timestamp', datetime.now())
    
    message = f"🎯 **Order Fill Summary**\n"
    message += f"Symbol: {symbol}\n"
    message += f"Side: {side.upper()}\n"
    message += f"Quantity: {quantity:,.2f}\n"
    message += f"Price: ${price:,.2f}\n"
    message += f"Value: ${(quantity * price):,.2f}\n"
    message += f"Time: {timestamp}"
    
    return message


def format_heartbeat_missed(last_heartbeat: datetime, current_time: datetime) -> str:
    """
    Format heartbeat missed notification.
    
    Args:
        last_heartbeat: Timestamp of last heartbeat
        current_time: Current timestamp
        
    Returns:
        Formatted message string
    """
    time_diff = current_time - last_heartbeat
    minutes = int(time_diff.total_seconds() / 60)
    
    message = f"⚠️ **Heartbeat Missed Alert**\n"
    message += f"Last heartbeat: {last_heartbeat.strftime('%Y-%m-%d %H:%M:%S')}\n"
    message += f"Current time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
    message += f"Time elapsed: {minutes} minutes\n"
    message += f"Status: System may be unresponsive"
    
    return message


# Convenience functions for specific notifications
async def notify_fill(fill: Dict[str, Any]) -> Dict[str, bool]:
    """Send fill notification."""
    message = format_fill_summary(fill)
    metadata = {
        'type': 'fill',
        'symbol': fill.get('symbol'),
        'side': fill.get('side'),
        'quantity': fill.get('quantity'),
        'price': fill.get('price')
    }
    
    return await send_alert(message, "Trading Bot - Order Fill", metadata)


async def notify_heartbeat_missed(last_heartbeat: datetime, current_time: datetime) -> Dict[str, bool]:
    """Send heartbeat missed notification."""
    message = format_heartbeat_missed(last_heartbeat, current_time)
    metadata = {
        'type': 'heartbeat_missed',
        'last_heartbeat': last_heartbeat.isoformat(),
        'current_time': current_time.isoformat(),
        'minutes_elapsed': int((current_time - last_heartbeat).total_seconds() / 60)
    }
    
    return await send_alert(message, "Trading Bot - Heartbeat Missed", metadata)