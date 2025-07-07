#!/usr/bin/env python3
"""
Debug script to identify performance bottlenecks in the SMA strategy.
This script will help diagnose why the SMA calculations are taking forever.
"""

import time
import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import cProfile
import pstats
from io import StringIO

# Add the external ai-hedge-fund to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'external', 'ai-hedge-fund'))

# Import the necessary modules
try:
    from src.tools.api import get_prices, prices_to_df
    from src.agents.technicals import (
        calculate_trend_signals,
        calculate_mean_reversion_signals,
        calculate_momentum_signals,
        calculate_volatility_signals,
        calculate_stat_arb_signals,
    )
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running this from the Trading-Bot directory")
    sys.exit(1)


def time_function(func, *args, **kwargs):
    """Time a function execution."""
    start = time.time()
    result = func(*args, **kwargs)
    end = time.time()
    return result, end - start


def profile_function(func, *args, **kwargs):
    """Profile a function to see where time is spent."""
    profiler = cProfile.Profile()
    profiler.enable()
    result = func(*args, **kwargs)
    profiler.disable()
    
    # Get the stats
    s = StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    ps.print_stats(20)  # Print top 20 time-consuming functions
    
    return result, s.getvalue()


def test_data_fetching(ticker="AAPL", days_back=30):
    """Test the performance of data fetching."""
    print(f"\n{'='*60}")
    print(f"Testing data fetching for {ticker}...")
    print(f"{'='*60}")
    
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    
    print(f"Date range: {start_date} to {end_date}")
    
    # Time the data fetching
    prices, fetch_time = time_function(get_prices, ticker, start_date, end_date)
    print(f"Data fetching took: {fetch_time:.2f} seconds")
    print(f"Number of price points: {len(prices)}")
    
    # Time the DataFrame conversion
    df, conversion_time = time_function(prices_to_df, prices)
    print(f"DataFrame conversion took: {conversion_time:.2f} seconds")
    print(f"DataFrame shape: {df.shape}")
    
    return df, fetch_time + conversion_time


def test_individual_strategies(prices_df):
    """Test each strategy function individually."""
    print(f"\n{'='*60}")
    print("Testing individual strategy functions...")
    print(f"{'='*60}")
    
    strategies = [
        ("Trend Signals", calculate_trend_signals),
        ("Mean Reversion Signals", calculate_mean_reversion_signals),
        ("Momentum Signals", calculate_momentum_signals),
        ("Volatility Signals", calculate_volatility_signals),
        ("Statistical Arbitrage Signals", calculate_stat_arb_signals),
    ]
    
    results = {}
    total_time = 0
    
    for name, func in strategies:
        print(f"\nTesting {name}...")
        try:
            result, exec_time = time_function(func, prices_df)
            results[name] = {
                "time": exec_time,
                "result": result
            }
            total_time += exec_time
            print(f"  Execution time: {exec_time:.2f} seconds")
            print(f"  Signal: {result['signal']}, Confidence: {result['confidence']:.2%}")
        except Exception as e:
            print(f"  ERROR: {e}")
            results[name] = {
                "time": 0,
                "error": str(e)
            }
    
    print(f"\nTotal time for all strategies: {total_time:.2f} seconds")
    return results


def test_rolling_window_performance(prices_df):
    """Test the performance of rolling window calculations."""
    print(f"\n{'='*60}")
    print("Testing rolling window calculations...")
    print(f"{'='*60}")
    
    close = prices_df["close"]
    
    # Test different window sizes
    windows = [20, 50, 100, 200]
    
    for window in windows:
        if len(close) >= window:
            # Test SMA calculation
            _, sma_time = time_function(lambda: close.rolling(window).mean())
            print(f"SMA {window}: {sma_time:.4f} seconds")
            
            # Test standard deviation calculation
            _, std_time = time_function(lambda: close.rolling(window).std())
            print(f"STD {window}: {std_time:.4f} seconds")
            
            # Test EMA calculation
            _, ema_time = time_function(lambda: close.ewm(span=window, adjust=False).mean())
            print(f"EMA {window}: {ema_time:.4f} seconds")
            
            print()


def profile_slowest_function(prices_df):
    """Profile the slowest function to identify bottlenecks."""
    print(f"\n{'='*60}")
    print("Profiling the slowest function...")
    print(f"{'='*60}")
    
    # Usually statistical arbitrage is one of the slowest
    print("\nProfiling calculate_stat_arb_signals...")
    _, profile_output = profile_function(calculate_stat_arb_signals, prices_df)
    print(profile_output)


def test_data_size_impact():
    """Test how data size impacts performance."""
    print(f"\n{'='*60}")
    print("Testing impact of data size on performance...")
    print(f"{'='*60}")
    
    ticker = "AAPL"
    data_sizes = [30, 60, 90, 180, 365]  # Days of data
    
    for days in data_sizes:
        print(f"\nTesting with {days} days of data...")
        
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        try:
            # Fetch data
            prices, _ = time_function(get_prices, ticker, start_date, end_date)
            df, _ = time_function(prices_to_df, prices)
            
            # Time a representative calculation
            _, calc_time = time_function(calculate_trend_signals, df)
            
            print(f"  Data points: {len(df)}")
            print(f"  Trend calculation time: {calc_time:.2f} seconds")
            
        except Exception as e:
            print(f"  ERROR: {e}")


def main():
    """Main debugging function."""
    print("SMA Strategy Performance Debugger")
    print("=================================")
    
    # Test 1: Data fetching
    prices_df, data_time = test_data_fetching("AAPL", 90)
    
    if prices_df.empty:
        print("ERROR: No data fetched. Cannot continue tests.")
        return
    
    # Test 2: Individual strategies
    strategy_results = test_individual_strategies(prices_df)
    
    # Test 3: Rolling window performance
    test_rolling_window_performance(prices_df)
    
    # Test 4: Profile the slowest function
    profile_slowest_function(prices_df)
    
    # Test 5: Data size impact
    test_data_size_impact()
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Data fetching time: {data_time:.2f} seconds")
    
    if strategy_results:
        print("\nStrategy execution times:")
        for name, result in strategy_results.items():
            if "error" in result:
                print(f"  {name}: ERROR - {result['error']}")
            else:
                print(f"  {name}: {result['time']:.2f} seconds")
    
    print("\nPotential bottlenecks identified:")
    
    # Identify bottlenecks
    bottlenecks = []
    
    if data_time > 5:
        bottlenecks.append("Data fetching is slow (>5 seconds)")
    
    for name, result in strategy_results.items():
        if "time" in result and result["time"] > 2:
            bottlenecks.append(f"{name} is slow (>{result['time']:.1f} seconds)")
    
    if bottlenecks:
        for bottleneck in bottlenecks:
            print(f"  - {bottleneck}")
    else:
        print("  No significant bottlenecks found in individual functions.")
        print("  The issue might be:")
        print("  - Running too many agents in sequence")
        print("  - Network latency in API calls")
        print("  - Large data volumes being processed")
        print("  - Memory constraints causing swapping")


if __name__ == "__main__":
    main()