#!/usr/bin/env python3
"""
Simplified test script for the SMA Agent without external dependencies.
"""

import asyncio
import time
import sys
import os
from datetime import datetime, timedelta
import random

# Add the trading_bot to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def simple_sma(prices, period):
    """Simple moving average calculation without numpy."""
    if len(prices) < period:
        return None
    return sum(prices[-period:]) / period

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
            'timestamp': timestamp,
            'open': base_price,
            'high': base_price * 1.02,
            'low': base_price * 0.98,
            'close': base_price,
            'volume': random.randint(1000, 10000)
        })
    
    return {
        'symbol': symbol,
        'current_price': base_price,
        'historical': historical,
        'timestamp': datetime.now()
    }

def test_sma_calculation():
    """Test the SMA calculation logic."""
    print("Testing SMA calculation...")
    
    # Test data
    prices = [100, 102, 98, 105, 103, 107, 104, 108, 106, 110]
    
    # Calculate SMAs
    sma_5 = simple_sma(prices, 5)
    sma_10 = simple_sma(prices, 10)
    
    print(f"Prices: {prices}")
    print(f"5-period SMA: {sma_5:.2f}")
    print(f"10-period SMA: {sma_10:.2f}")
    
    # Test crossover detection
    prev_prices = [100, 102, 98, 105, 103, 107, 104, 108, 106]
    prev_sma_5 = simple_sma(prev_prices, 5)
    
    print(f"\nCrossover test:")
    print(f"Previous 5-SMA: {prev_sma_5:.2f}")
    print(f"Current 5-SMA: {sma_5:.2f}")
    print(f"Current 10-SMA: {sma_10:.2f}")
    
    if prev_sma_5 < sma_10 and sma_5 > sma_10:
        print("📈 BULLISH CROSSOVER DETECTED!")
    elif prev_sma_5 > sma_10 and sma_5 < sma_10:
        print("📉 BEARISH CROSSOVER DETECTED!")
    else:
        print("No crossover detected")

def test_performance():
    """Test performance with large dataset."""
    print("\n" + "="*50)
    print("PERFORMANCE TEST")
    print("="*50)
    
    # Generate large dataset
    num_points = 10000
    print(f"Generating {num_points} data points...")
    
    start_time = time.time()
    mock_data = generate_mock_price_data("TEST", num_points)
    generation_time = time.time() - start_time
    
    print(f"Data generation time: {generation_time:.4f} seconds")
    
    # Extract prices
    prices = [point['close'] for point in mock_data['historical']]
    
    # Test SMA calculations
    start_time = time.time()
    
    sma_results = []
    for i in range(20, len(prices)):  # Start after we have enough data
        sma_10 = simple_sma(prices[:i+1], 10)
        sma_20 = simple_sma(prices[:i+1], 20)
        sma_results.append((sma_10, sma_20))
    
    calc_time = time.time() - start_time
    
    print(f"SMA calculations for {len(sma_results)} points: {calc_time:.4f} seconds")
    print(f"Average time per calculation: {calc_time/len(sma_results)*1000:.4f} ms")
    
    # Show sample results
    print(f"\nSample results (last 5):")
    for i, (sma_10, sma_20) in enumerate(sma_results[-5:]):
        print(f"  Point {len(sma_results)-5+i}: SMA10={sma_10:.2f}, SMA20={sma_20:.2f}")

def main():
    """Run all tests."""
    print("SMA Agent Performance Test")
    print("="*50)
    
    try:
        test_sma_calculation()
        test_performance()
        
        print("\n" + "="*50)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*50)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()