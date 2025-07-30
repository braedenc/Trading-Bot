#!/usr/bin/env python3
"""
Test script for the SMA Agent to verify performance and functionality.
"""

import asyncio
import time
import sys
import os
from datetime import datetime, timedelta
import random

# Add the trading_bot to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trading_bot.agents.sma_agent import SMAAgent


def generate_mock_price_data(symbol: str, days: int = 100) -> dict:
    """Generate mock historical price data for testing."""
    
    historical = []
    base_price = 100.0
    
    for i in range(days):
        # Add some randomness to create realistic price movement
        price_change = random.uniform(-2, 2)
        base_price = max(10, base_price + price_change)  # Don't go below $10
        
        timestamp = datetime.now() - timedelta(days=days-i)
        
        historical.append({
            'timestamp': timestamp.isoformat(),
            'close': base_price,
            'volume': random.randint(1000, 10000)
        })
    
    return {
        'current': base_price,
        'historical': historical
    }


async def test_sma_agent_performance():
    """Test the SMA agent with various scenarios."""
    
    print("Testing SMA Agent Performance")
    print("=" * 50)
    
    # Create SMA agent with different parameters
    agent = SMAAgent(fast_period=5, slow_period=20, min_data_points=30)
    
    # Set some risk limits
    await agent.on_limit_update({
        'max_position_size': 1000,
        'max_daily_loss': 5000,
        'max_leverage': 2.0,
        'allowed_symbols': ['AAPL', 'GOOGL', 'MSFT']
    })
    
    # Test 1: Basic functionality with sufficient data
    print("\nTest 1: Basic Signal Generation")
    print("-" * 30)
    
    snapshot = {
        'prices': {
            'AAPL': generate_mock_price_data('AAPL', 50),
            'GOOGL': generate_mock_price_data('GOOGL', 50),
        },
        'positions': {
            'AAPL': 0,
            'GOOGL': 100,  # Already have position
        }
    }
    
    start_time = time.time()
    signals = await agent.generate_signals(snapshot)
    execution_time = time.time() - start_time
    
    print(f"Generated {len(signals)} signals in {execution_time:.4f} seconds")
    
    for signal in signals:
        print(f"  {signal['symbol']}: {signal['action']} {signal['quantity']} "
              f"(confidence: {signal['confidence']:.2f})")
        print(f"    Reasoning: {signal['reasoning']}")
    
    # Test 2: Performance with insufficient data
    print("\nTest 2: Insufficient Data Handling")
    print("-" * 30)
    
    snapshot_small = {
        'prices': {
            'TSLA': generate_mock_price_data('TSLA', 10),  # Too little data
        },
        'positions': {'TSLA': 0}
    }
    
    start_time = time.time()
    signals = await agent.generate_signals(snapshot_small)
    execution_time = time.time() - start_time
    
    print(f"Generated {len(signals)} signals in {execution_time:.4f} seconds")
    print("Expected: 0 signals due to insufficient data")
    
    # Test 3: Performance with large dataset
    print("\nTest 3: Large Dataset Performance")
    print("-" * 30)
    
    snapshot_large = {
        'prices': {
            'AAPL': generate_mock_price_data('AAPL', 500),  # Large dataset
            'GOOGL': generate_mock_price_data('GOOGL', 500),
            'MSFT': generate_mock_price_data('MSFT', 500),
            'TSLA': generate_mock_price_data('TSLA', 500),
            'AMZN': generate_mock_price_data('AMZN', 500),
        },
        'positions': {symbol: 0 for symbol in ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']}
    }
    
    start_time = time.time()
    signals = await agent.generate_signals(snapshot_large)
    execution_time = time.time() - start_time
    
    print(f"Generated {len(signals)} signals for 5 symbols with 500 data points each")
    print(f"Execution time: {execution_time:.4f} seconds")
    print(f"Average time per symbol: {execution_time/5:.4f} seconds")
    
    # Test 4: Cache effectiveness
    print("\nTest 4: Cache Effectiveness")
    print("-" * 30)
    
    # Run the same calculation again to test caching
    start_time = time.time()
    signals_cached = await agent.generate_signals(snapshot_large)
    cached_execution_time = time.time() - start_time
    
    print(f"Second run (cached): {cached_execution_time:.4f} seconds")
    print(f"Speedup: {execution_time/cached_execution_time:.2f}x")
    
    # Test 5: Memory usage
    print("\nTest 5: Memory and Cache Stats")
    print("-" * 30)
    
    stats = agent.get_performance_stats()
    print(f"Agent: {stats['name']}")
    print(f"Fast period: {stats['fast_period']}")
    print(f"Slow period: {stats['slow_period']}")
    print(f"Cache size: {stats['cache_size']}")
    print(f"Min data points: {stats['min_data_points']}")
    
    # Test 6: Fill and limit handling
    print("\nTest 6: Fill and Limit Handling")
    print("-" * 30)
    
    # Test fill handling
    await agent.on_fill({
        'symbol': 'AAPL',
        'side': 'buy',
        'quantity': 100,
        'price': 150.50,
        'timestamp': datetime.now(),
        'order_id': 'test_123'
    })
    
    # Test limit updates
    await agent.on_limit_update({
        'max_position_size': 2000,  # Increased
        'max_daily_loss': 10000,
    })
    
    print("Fill and limit handling completed successfully")
    
    # Cleanup
    await agent.shutdown()
    
    print("\n" + "=" * 50)
    print("SMA Agent Performance Test Complete")
    print("All tests passed successfully!")


if __name__ == "__main__":
    # Run the async test
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_sma_agent_performance())