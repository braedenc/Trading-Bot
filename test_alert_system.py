"""
Tests for the alert system.
Uses httpx_mock for Slack webhook testing and aiosmtplib monkeypatch for email testing.
"""

import pytest
import asyncio
import os
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from typing import Dict, Any

# Mock dependencies that might not be available
mock_httpx = MagicMock()
mock_aiosmtplib = MagicMock()
mock_email = MagicMock()

# Set up the mocks before importing tools
import sys
sys.modules['httpx'] = mock_httpx
sys.modules['aiosmtplib'] = mock_aiosmtplib
sys.modules['email.mime.text'] = mock_email
sys.modules['email.mime.multipart'] = mock_email

# Now import the actual modules we want to test
from tools.alert import (
    send_slack,
    send_email,
    send_alert,
    notify_fill,
    notify_heartbeat_missed,
    format_fill_summary,
    format_heartbeat_missed,
    AlertConfig,
    config
)

from tools.heartbeat import (
    HeartbeatManager,
    heartbeat_manager,
    start_heartbeat_monitoring,
    stop_heartbeat_monitoring,
    register_heartbeat_source,
    send_heartbeat,
    deregister_heartbeat_source,
    get_heartbeat_status
)


class TestAlertConfig:
    """Test AlertConfig class."""
    
    def test_init_with_env_vars(self):
        """Test AlertConfig initialization with environment variables."""
        with patch.dict(os.environ, {
            'SLACK_WEBHOOK_URL': 'https://hooks.slack.com/test',
            'SMTP_SERVER': 'smtp.test.com',
            'SMTP_PORT': '587',
            'SMTP_USERNAME': 'test@test.com',
            'SMTP_PASSWORD': 'password',
            'EMAIL_FROM': 'from@test.com',
            'EMAIL_TO': 'to@test.com'
        }):
            config = AlertConfig()
            assert config.slack_webhook_url == 'https://hooks.slack.com/test'
            assert config.smtp_server == 'smtp.test.com'
            assert config.smtp_port == 587
            assert config.smtp_username == 'test@test.com'
            assert config.smtp_password == 'password'
            assert config.email_from == 'from@test.com'
            assert config.email_to == 'to@test.com'
    
    def test_init_without_env_vars(self):
        """Test AlertConfig initialization without environment variables."""
        with patch.dict(os.environ, {}, clear=True):
            config = AlertConfig()
            assert config.slack_webhook_url is None
            assert config.smtp_server == 'smtp.gmail.com'
            assert config.smtp_port == 587
            assert config.smtp_username is None
            assert config.smtp_password is None
            assert config.email_from is None
            assert config.email_to is None
    
    def test_slack_enabled_property(self):
        """Test slack_enabled property."""
        # Mock httpx to be available
        with patch('tools.alert.httpx', mock_httpx):
            with patch.dict(os.environ, {'SLACK_WEBHOOK_URL': 'https://hooks.slack.com/test'}):
                config = AlertConfig()
                assert config.slack_enabled is True
        
        # Test without webhook URL
        with patch.dict(os.environ, {}, clear=True):
            config = AlertConfig()
            assert config.slack_enabled is False
    
    def test_email_enabled_property(self):
        """Test email_enabled property."""
        # Mock email modules to be available
        with patch('tools.alert.aiosmtplib', mock_aiosmtplib):
            with patch('tools.alert.MIMEText', mock_email):
                with patch('tools.alert.MIMEMultipart', mock_email):
                    with patch.dict(os.environ, {
                        'SMTP_USERNAME': 'test@test.com',
                        'SMTP_PASSWORD': 'password',
                        'EMAIL_FROM': 'from@test.com',
                        'EMAIL_TO': 'to@test.com'
                    }):
                        config = AlertConfig()
                        assert config.email_enabled is True
        
        # Test without credentials
        with patch.dict(os.environ, {}, clear=True):
            config = AlertConfig()
            assert config.email_enabled is False


class TestSlackNotifications:
    """Test Slack notification functionality."""
    
    @pytest.fixture
    def mock_httpx_client(self):
        """Mock httpx client for testing."""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_client.post.return_value = mock_response
        return mock_client
    
    @pytest.mark.asyncio
    async def test_send_slack_success(self, mock_httpx_client):
        """Test successful Slack notification."""
        with patch('tools.alert.httpx') as mock_httpx:
            with patch.dict(os.environ, {'SLACK_WEBHOOK_URL': 'https://hooks.slack.com/test'}):
                mock_httpx.AsyncClient.return_value.__aenter__.return_value = mock_httpx_client
                
                result = await send_slack("Test message")
                
                assert result is True
                mock_httpx_client.post.assert_called_once()
                call_args = mock_httpx_client.post.call_args
                assert call_args[0][0] == 'https://hooks.slack.com/test'
                assert call_args[1]['json']['text'] == 'Test message'
    
    @pytest.mark.asyncio
    async def test_send_slack_with_metadata(self, mock_httpx_client):
        """Test Slack notification with metadata."""
        with patch('tools.alert.httpx') as mock_httpx:
            with patch.dict(os.environ, {'SLACK_WEBHOOK_URL': 'https://hooks.slack.com/test'}):
                mock_httpx.AsyncClient.return_value.__aenter__.return_value = mock_httpx_client
                
                metadata = {'symbol': 'AAPL', 'price': 150.0}
                result = await send_slack("Test message", metadata)
                
                assert result is True
                call_args = mock_httpx_client.post.call_args
                payload = call_args[1]['json']
                assert 'attachments' in payload
                assert len(payload['attachments']) == 1
                assert payload['attachments'][0]['color'] == 'good'
    
    @pytest.mark.asyncio
    async def test_send_slack_no_webhook_url(self):
        """Test Slack notification without webhook URL."""
        with patch.dict(os.environ, {}, clear=True):
            result = await send_slack("Test message")
            assert result is False
    
    @pytest.mark.asyncio
    async def test_send_slack_http_error(self, mock_httpx_client):
        """Test Slack notification with HTTP error."""
        with patch('tools.alert.httpx') as mock_httpx:
            with patch.dict(os.environ, {'SLACK_WEBHOOK_URL': 'https://hooks.slack.com/test'}):
                mock_httpx.AsyncClient.return_value.__aenter__.return_value = mock_httpx_client
                mock_httpx_client.post.side_effect = Exception("HTTP Error")
                
                result = await send_slack("Test message")
                
                assert result is False


class TestEmailNotifications:
    """Test email notification functionality."""
    
    @pytest.fixture
    def mock_smtp_server(self):
        """Mock SMTP server for testing."""
        mock_server = AsyncMock()
        mock_server.starttls = AsyncMock()
        mock_server.login = AsyncMock()
        mock_server.send_message = AsyncMock()
        return mock_server
    
    @pytest.mark.asyncio
    async def test_send_email_success(self, mock_smtp_server):
        """Test successful email notification."""
        with patch('tools.alert.aiosmtplib') as mock_aiosmtplib:
            with patch('tools.alert.MIMEText') as mock_mime_text:
                with patch('tools.alert.MIMEMultipart') as mock_mime_multipart:
                    with patch.dict(os.environ, {
                        'SMTP_USERNAME': 'test@test.com',
                        'SMTP_PASSWORD': 'password',
                        'EMAIL_FROM': 'from@test.com',
                        'EMAIL_TO': 'to@test.com'
                    }):
                        mock_aiosmtplib.SMTP.return_value.__aenter__.return_value = mock_smtp_server
                        mock_msg = MagicMock()
                        mock_mime_multipart.return_value = mock_msg
                        
                        result = await send_email("Test message", "Test Subject")
                        
                        assert result is True
                        mock_smtp_server.starttls.assert_called_once()
                        mock_smtp_server.login.assert_called_once_with('test@test.com', 'password')
                        mock_smtp_server.send_message.assert_called_once_with(mock_msg)
    
    @pytest.mark.asyncio
    async def test_send_email_with_metadata(self, mock_smtp_server):
        """Test email notification with metadata."""
        with patch('tools.alert.aiosmtplib') as mock_aiosmtplib:
            with patch('tools.alert.MIMEText') as mock_mime_text:
                with patch('tools.alert.MIMEMultipart') as mock_mime_multipart:
                    with patch.dict(os.environ, {
                        'SMTP_USERNAME': 'test@test.com',
                        'SMTP_PASSWORD': 'password',
                        'EMAIL_FROM': 'from@test.com',
                        'EMAIL_TO': 'to@test.com'
                    }):
                        mock_aiosmtplib.SMTP.return_value.__aenter__.return_value = mock_smtp_server
                        mock_msg = MagicMock()
                        mock_mime_multipart.return_value = mock_msg
                        
                        metadata = {'symbol': 'AAPL', 'price': 150.0}
                        result = await send_email("Test message", "Test Subject", metadata)
                        
                        assert result is True
                        # Check that metadata is included in the email body
                        mock_mime_text.assert_called_once()
                        body_text = mock_mime_text.call_args[0][0]
                        assert 'Additional Information:' in body_text
                        assert 'symbol: AAPL' in body_text
                        assert 'price: 150.0' in body_text
    
    @pytest.mark.asyncio
    async def test_send_email_no_config(self):
        """Test email notification without configuration."""
        with patch.dict(os.environ, {}, clear=True):
            result = await send_email("Test message")
            assert result is False
    
    @pytest.mark.asyncio
    async def test_send_email_smtp_error(self, mock_smtp_server):
        """Test email notification with SMTP error."""
        with patch('tools.alert.aiosmtplib') as mock_aiosmtplib:
            with patch('tools.alert.MIMEText') as mock_mime_text:
                with patch('tools.alert.MIMEMultipart') as mock_mime_multipart:
                    with patch.dict(os.environ, {
                        'SMTP_USERNAME': 'test@test.com',
                        'SMTP_PASSWORD': 'password',
                        'EMAIL_FROM': 'from@test.com',
                        'EMAIL_TO': 'to@test.com'
                    }):
                        mock_aiosmtplib.SMTP.return_value.__aenter__.return_value = mock_smtp_server
                        mock_smtp_server.send_message.side_effect = Exception("SMTP Error")
                        
                        result = await send_email("Test message")
                        
                        assert result is False


class TestAlertFormatting:
    """Test alert formatting functions."""
    
    def test_format_fill_summary(self):
        """Test fill summary formatting."""
        fill = {
            'symbol': 'AAPL',
            'side': 'buy',
            'quantity': 100,
            'price': 150.0,
            'timestamp': datetime(2023, 1, 1, 12, 0, 0)
        }
        
        result = format_fill_summary(fill)
        
        assert '🎯 **Order Fill Summary**' in result
        assert 'Symbol: AAPL' in result
        assert 'Side: BUY' in result
        assert 'Quantity: 100.00' in result
        assert 'Price: $150.00' in result
        assert 'Value: $15,000.00' in result
        assert '2023-01-01 12:00:00' in result
    
    def test_format_heartbeat_missed(self):
        """Test heartbeat missed formatting."""
        last_heartbeat = datetime(2023, 1, 1, 12, 0, 0)
        current_time = datetime(2023, 1, 1, 12, 15, 0)
        
        result = format_heartbeat_missed(last_heartbeat, current_time)
        
        assert '⚠️ **Heartbeat Missed Alert**' in result
        assert 'Last heartbeat: 2023-01-01 12:00:00' in result
        assert 'Current time: 2023-01-01 12:15:00' in result
        assert 'Time elapsed: 15 minutes' in result
        assert 'Status: System may be unresponsive' in result


class TestConvenienceFunctions:
    """Test convenience notification functions."""
    
    @pytest.mark.asyncio
    async def test_notify_fill(self):
        """Test notify_fill function."""
        with patch('tools.alert.send_alert') as mock_send_alert:
            mock_send_alert.return_value = {'slack': True, 'email': False}
            
            fill = {
                'symbol': 'AAPL',
                'side': 'buy',
                'quantity': 100,
                'price': 150.0
            }
            
            result = await notify_fill(fill)
            
            assert result == {'slack': True, 'email': False}
            mock_send_alert.assert_called_once()
            call_args = mock_send_alert.call_args
            assert 'Order Fill Summary' in call_args[0][0]
            assert call_args[1]['subject'] == 'Trading Bot - Order Fill'
            assert call_args[1]['metadata']['type'] == 'fill'
    
    @pytest.mark.asyncio
    async def test_notify_heartbeat_missed(self):
        """Test notify_heartbeat_missed function."""
        with patch('tools.alert.send_alert') as mock_send_alert:
            mock_send_alert.return_value = {'slack': True, 'email': True}
            
            last_heartbeat = datetime(2023, 1, 1, 12, 0, 0)
            current_time = datetime(2023, 1, 1, 12, 15, 0)
            
            result = await notify_heartbeat_missed(last_heartbeat, current_time)
            
            assert result == {'slack': True, 'email': True}
            mock_send_alert.assert_called_once()
            call_args = mock_send_alert.call_args
            assert 'Heartbeat Missed Alert' in call_args[0][0]
            assert call_args[1]['subject'] == 'Trading Bot - Heartbeat Missed'
            assert call_args[1]['metadata']['type'] == 'heartbeat_missed'


class TestHeartbeatManager:
    """Test heartbeat manager functionality."""
    
    @pytest.fixture
    def heartbeat_manager(self):
        """Create a fresh heartbeat manager for testing."""
        return HeartbeatManager(heartbeat_timeout=1)  # 1 minute timeout for testing
    
    @pytest.mark.asyncio
    async def test_register_source(self, heartbeat_manager):
        """Test registering a heartbeat source."""
        await heartbeat_manager.register_source("test_agent")
        
        assert "test_agent" in heartbeat_manager.heartbeats
        status = heartbeat_manager.heartbeats["test_agent"]
        assert status.name == "test_agent"
        assert status.is_active is True
        assert status.missed_count == 0
    
    @pytest.mark.asyncio
    async def test_heartbeat(self, heartbeat_manager):
        """Test sending a heartbeat."""
        await heartbeat_manager.heartbeat("test_agent")
        
        assert "test_agent" in heartbeat_manager.heartbeats
        status = heartbeat_manager.heartbeats["test_agent"]
        assert status.is_active is True
        assert status.missed_count == 0
    
    @pytest.mark.asyncio
    async def test_deregister_source(self, heartbeat_manager):
        """Test deregistering a heartbeat source."""
        await heartbeat_manager.register_source("test_agent")
        await heartbeat_manager.deregister_source("test_agent")
        
        assert "test_agent" not in heartbeat_manager.heartbeats
    
    @pytest.mark.asyncio
    async def test_heartbeat_timeout(self, heartbeat_manager):
        """Test heartbeat timeout detection."""
        with patch('tools.heartbeat.notify_heartbeat_missed') as mock_notify:
            await heartbeat_manager.register_source("test_agent")
            
            # Simulate heartbeat timeout by manually setting old timestamp
            status = heartbeat_manager.heartbeats["test_agent"]
            status.last_heartbeat = datetime.now() - timedelta(minutes=2)
            
            await heartbeat_manager._check_heartbeats()
            
            assert status.is_active is False
            assert status.missed_count == 1
            mock_notify.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_start_stop_monitoring(self, heartbeat_manager):
        """Test starting and stopping heartbeat monitoring."""
        await heartbeat_manager.start_monitoring()
        assert heartbeat_manager.is_running is True
        assert heartbeat_manager._monitor_task is not None
        
        await heartbeat_manager.stop_monitoring()
        assert heartbeat_manager.is_running is False
    
    def test_get_status(self, heartbeat_manager):
        """Test getting heartbeat status."""
        asyncio.run(heartbeat_manager.register_source("test_agent"))
        
        status = heartbeat_manager.get_status()
        
        assert "test_agent" in status
        agent_status = status["test_agent"]
        assert agent_status['name'] == "test_agent"
        assert agent_status['is_active'] is True
        assert agent_status['missed_count'] == 0
        assert 'minutes_since_last' in agent_status
        assert 'is_overdue' in agent_status


class TestIntegrationWithMocks:
    """Integration tests with mocked dependencies."""
    
    @pytest.mark.asyncio
    async def test_place_order_with_slack_webhook(self):
        """Test that placing an order hits mocked Slack endpoint when SLACK_WEBHOOK_URL is set."""
        with patch('tools.alert.httpx') as mock_httpx:
            with patch.dict(os.environ, {'SLACK_WEBHOOK_URL': 'https://hooks.slack.com/test'}):
                mock_client = AsyncMock()
                mock_response = MagicMock()
                mock_response.raise_for_status = MagicMock()
                mock_client.post.return_value = mock_response
                mock_httpx.AsyncClient.return_value.__aenter__.return_value = mock_client
                
                # Simulate order fill
                fill = {
                    'symbol': 'AAPL',
                    'side': 'buy',
                    'quantity': 100,
                    'price': 150.0,
                    'timestamp': datetime.now()
                }
                
                result = await notify_fill(fill)
                
                # Verify Slack endpoint was called
                assert result.get('slack') is True
                mock_client.post.assert_called_once()
                call_args = mock_client.post.call_args
                assert call_args[0][0] == 'https://hooks.slack.com/test'
                assert 'Order Fill Summary' in call_args[1]['json']['text']
    
    @pytest.mark.asyncio
    async def test_missing_webhook_env_silently_skips(self):
        """Test that missing webhook env silently skips with log."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('tools.alert.logger') as mock_logger:
                result = await send_slack("Test message")
                
                assert result is False
                mock_logger.debug.assert_called_once_with(
                    "Slack webhook URL not configured, skipping Slack notification"
                )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])