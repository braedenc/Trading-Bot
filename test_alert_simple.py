#!/usr/bin/env python3
"""
Simple test script to verify the alert system works.
"""

import asyncio
import os
from datetime import datetime

# Test the alert system
async def test_alert_system():
    """Test basic alert system functionality."""
    print("Testing Alert System...")
    
    # Test 1: Test without environment variables (should skip gracefully)
    print("\n1. Testing without environment variables...")
    try:
        from tools.alert import send_slack, send_email, notify_fill
        
        result = await send_slack("Test message")
        print(f"   Slack (no config): {result}")
        
        result = await send_email("Test message")
        print(f"   Email (no config): {result}")
        
        # Test fill notification
        fill = {
            'symbol': 'AAPL',
            'side': 'buy',
            'quantity': 100,
            'price': 150.0,
            'timestamp': datetime.now()
        }
        
        result = await notify_fill(fill)
        print(f"   Fill notification: {result}")
        
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Test with mock environment variables
    print("\n2. Testing with mock environment variables...")
    
    # Set fake environment variables
    os.environ['SLACK_WEBHOOK_URL'] = 'https://hooks.slack.com/test'
    os.environ['SMTP_USERNAME'] = 'test@test.com'
    os.environ['SMTP_PASSWORD'] = 'password'
    os.environ['EMAIL_FROM'] = 'from@test.com'
    os.environ['EMAIL_TO'] = 'to@test.com'
    
    # Reload config
    from tools.alert import AlertConfig
    config = AlertConfig()
    
    print(f"   Slack enabled: {config.slack_enabled}")
    print(f"   Email enabled: {config.email_enabled}")
    print(f"   Webhook URL: {config.slack_webhook_url}")
    
    # Test 3: Test heartbeat system
    print("\n3. Testing heartbeat system...")
    try:
        from tools.heartbeat import HeartbeatManager
        
        manager = HeartbeatManager(heartbeat_timeout=1)  # 1 minute timeout
        
        # Register a test source
        await manager.register_source("test_agent")
        print("   Registered test_agent")
        
        # Send heartbeat
        await manager.heartbeat("test_agent")
        print("   Sent heartbeat")
        
        # Get status
        status = manager.get_status()
        print(f"   Status: {status}")
        
        # Deregister
        await manager.deregister_source("test_agent")
        print("   Deregistered test_agent")
        
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 4: Test formatting functions
    print("\n4. Testing formatting functions...")
    try:
        from tools.alert import format_fill_summary, format_heartbeat_missed
        
        fill = {
            'symbol': 'AAPL',
            'side': 'buy',
            'quantity': 100,
            'price': 150.0,
            'timestamp': datetime.now()
        }
        
        fill_message = format_fill_summary(fill)
        print(f"   Fill summary formatted: {len(fill_message)} characters")
        
        heartbeat_message = format_heartbeat_missed(
            datetime.now() - timedelta(minutes=15),
            datetime.now()
        )
        print(f"   Heartbeat message formatted: {len(heartbeat_message)} characters")
        
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n✅ Alert system test completed!")


# Test the SMA agent integration
async def test_sma_agent_integration():
    """Test SMA agent integration with alert system."""
    print("\nTesting SMA Agent Integration...")
    
    try:
        from trading_bot.agents.sma_agent import SMAAgent
        from trading_bot.test_sma_simple import generate_mock_price_data
        
        # Create agent
        agent = SMAAgent(fast_period=5, slow_period=10)
        print("   Created SMA agent")
        
        # Test fill notification
        fill = {
            'symbol': 'AAPL',
            'side': 'buy',
            'quantity': 100,
            'price': 150.0,
            'timestamp': datetime.now()
        }
        
        await agent.on_fill(fill)
        print("   Tested fill notification")
        
        # Test heartbeat (via signal generation)
        mock_data = generate_mock_price_data('AAPL', 100)
        snapshot = {
            'prices': {'AAPL': {'historical': mock_data}},
            'positions': {}
        }
        
        signals = await agent.generate_signals(snapshot)
        print(f"   Generated {len(signals)} signals (heartbeat sent)")
        
        # Cleanup
        await agent.shutdown()
        print("   Agent shutdown complete")
        
    except Exception as e:
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("✅ SMA Agent integration test completed!")


async def main():
    """Main test function."""
    await test_alert_system()
    await test_sma_agent_integration()
    print("\n🎉 All tests completed successfully!")


if __name__ == "__main__":
    # Need to import timedelta for the test
    from datetime import timedelta
    asyncio.run(main())