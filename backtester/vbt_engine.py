#!/usr/bin/env python3
"""
VectorBT Backtesting Engine
---------------------------
Runs backtests using vectorbt and generates performance reports.
"""

import sys
from pathlib import Path

# Add the project root to the Python path to find custom modules
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / 'src'))

print(f"[vbt_engine] project_root: {project_root}")
print(f"[vbt_engine] sys.path after modification: {sys.path}")

import argparse
import os
from datetime import datetime, timedelta
import yfinance as yf
import vectorbt as vbt
import pandas as pd
import numpy as np
import time
import requests

from strategies.example_backtest_strategy import ExampleBacktestStrategy
from strategies.githubagent_strategy import GitHubAgentStrategy

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run vectorbt backtest')
    parser.add_argument('--symbols', nargs='+', required=True,
                      help='List of symbols to backtest')
    parser.add_argument('--start', required=True,
                      help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', required=True,
                      help='End date (YYYY-MM-DD)')
    parser.add_argument('--strategy', default='example',
                      help='Strategy to use (default: example)')
    return parser.parse_args()

def test_yfinance():
    """Test if yfinance is working correctly."""
    print("\nTesting yfinance connection...")
    try:
        # First test if we can access Yahoo Finance
        try:
            response = requests.get('https://finance.yahoo.com', timeout=10)
            if response.status_code != 200:
                print(f"Warning: Yahoo Finance website returned status code {response.status_code}")
                print("This might indicate network or proxy issues.")
        except requests.exceptions.RequestException as e:
            print(f"Warning: Could not connect to Yahoo Finance website: {str(e)}")
            print("This might indicate network or proxy issues.")
        
        # Try to get data for a simple symbol with a longer timeout
        print("\nAttempting to download test data...")
        df = yf.download(
            'SPY',
            period='1d',
            progress=False,
            timeout=30
        )
        
        if not df.empty:
            print("yfinance test successful!")
            print(f"Got data for SPY: {df.head()}")
            return True
        else:
            print("yfinance test failed: No data returned")
            print("\nTroubleshooting steps:")
            print("1. Check your internet connection")
            print("2. Try accessing finance.yahoo.com in your browser")
            print("3. If using a proxy, make sure it's configured correctly")
            print("4. Try running: pip install --upgrade yfinance requests pandas numpy")
            return False
    except Exception as e:
        print(f"yfinance test failed with error: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Check your internet connection")
        print("2. Try accessing finance.yahoo.com in your browser")
        print("3. If using a proxy, make sure it's configured correctly")
        print("4. Try running: pip install --upgrade yfinance requests pandas numpy")
        return False

def download_data(symbols, start, end):
    """Download OHLCV data for symbols."""
    print(f"Downloading data for {symbols}...")
    data = {}
    
    # First test if yfinance is working
    if not test_yfinance():
        print("\nWARNING: yfinance test failed. Please check your installation:")
        print("1. Try reinstalling yfinance: pip install --upgrade yfinance")
        print("2. Check your internet connection")
        print("3. Verify you can access finance.yahoo.com")
        print("4. If using a proxy, make sure it's configured correctly")
        return data
    
    # Convert string dates to datetime objects
    try:
        start_date = datetime.strptime(start, '%Y-%m-%d')
        end_date = datetime.strptime(end, '%Y-%m-%d')
    except ValueError as e:
        print(f"Error parsing dates: {e}")
        print("Using default date range (last 365 days)")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
    
    print(f"Using date range: {start_date.date()} to {end_date.date()}")
    
    for symbol in symbols:
        try:
            print(f"\nAttempting to download data for {symbol}...")
            
            # Try downloading with retries
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    df = yf.download(
                        symbol,
                        start=start_date,
                        end=end_date,
                        progress=False,
                        interval="1d",
                        ignore_tz=True,
                        timeout=30
                    )
                    
                    if not df.empty:
                        print(f"Successfully downloaded {len(df)} days of data for {symbol}")
                        print(f"Date range: {df.index[0]} to {df.index[-1]}")
                        print(f"Columns available: {df.columns.tolist()}")
                        print(f"First few rows:\n{df.head()}")
                        data[symbol] = df
                        break
                    else:
                        print(f"Attempt {attempt + 1}: No data found for {symbol}")
                        if attempt < max_retries - 1:
                            print("Retrying in 2 seconds...")
                            time.sleep(2)
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed: {str(e)}")
                    if attempt < max_retries - 1:
                        print("Retrying in 2 seconds...")
                        time.sleep(2)
            
        except Exception as e:
            print(f"Error downloading data for {symbol}: {str(e)}")
            continue
    
    if not data:
        print("\nNo data was downloaded for any symbols. Please check:")
        print("1. Your internet connection")
        print("2. The symbol names are correct")
        print("3. The market was open during the specified period")
        print("4. If using a proxy, make sure it's configured correctly")
        print("\nTrying alternative symbols...")
        # Try some alternative symbols that are known to work
        alt_symbols = ['SPY', 'QQQ']
        print(f"Attempting to download data for alternative symbols: {alt_symbols}")
        for symbol in alt_symbols:
            try:
                df = yf.download(
                    symbol,
                    start=start_date,
                    end=end_date,
                    progress=False,
                    interval="1d",
                    ignore_tz=True,
                    timeout=30
                )
                if not df.empty:
                    print(f"Successfully downloaded data for {symbol}")
                    data[symbol] = df
            except Exception as e:
                print(f"Failed to download {symbol}: {str(e)}")
    
    return data

def run_backtest(data, strategy_name='example'):
    """Run backtest using specified strategy."""
    # Initialize strategy
    if strategy_name.lower() == 'examplebackteststrategy':
        strategy = ExampleBacktestStrategy()
    elif strategy_name.lower() == 'githubagentstrategy':
        # For backtesting, we always want 'array' return type
        strategy = GitHubAgentStrategy(strategy_config={'return_type': 'array'})
    else:
        raise ValueError(f"Unknown strategy: {strategy_name}")
    
    # Generate signals for each symbol
    entries = {}
    exits = {}
    for symbol, df in data.items():
        # Set the symbol name on the DataFrame
        df.name = symbol
        result = strategy.generate_signals(df)
        
        # Handle different signal formats
        if isinstance(result, dict):
            entries[symbol] = result["entry"]
            exits[symbol] = result["exit"]
        elif isinstance(result, str):
            # Convert string signals to boolean Series
            entries[symbol] = pd.Series(result.lower() == "buy", index=df.index)
            exits[symbol] = pd.Series(result.lower() == "sell", index=df.index)
        else:
            raise ValueError("Unknown signal format")
    
    # Convert to vectorbt format
    entries = pd.DataFrame(entries)
    exits = pd.DataFrame(exits)
    close = pd.DataFrame({symbol: df['Close'] for symbol, df in data.items()})
    
    # Create portfolio
    portfolio = vbt.Portfolio.from_signals(
        close=close,
        entries=entries,
        exits=exits,
        init_cash=100000,  # Starting with $100k
        fees=0.001,  # 0.1% trading fee
        freq='1D'  # Daily frequency
    )
    
    return portfolio

def generate_report(portfolio, output_dir='logs'):
    """Generate and save performance report."""
    try:
        print("\nStarting report generation...")
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        print(f"Output directory: {os.path.abspath(output_dir)}")
        
        # Calculate key metrics
        print("Calculating metrics...")
        total_return = portfolio.total_return().mean()  # Take mean of returns
        sharpe_ratio = portfolio.sharpe_ratio().mean()  # Take mean of Sharpe ratios
        max_drawdown = portfolio.max_drawdown().max()  # Take max of drawdowns
        
        # Print metrics
        print("\nBacktest Results:")
        print(f"Total Return: {total_return:.2%}")
        print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
        print(f"Max Drawdown: {max_drawdown:.2%}")
        
        # Generate and save HTML report
        report_path = Path(output_dir) / 'backtest_report.html'
        print(f"\nGenerating report at: {report_path.absolute()}")
        
        # Create the plot with column specification
        print("Creating plot...")
        fig = portfolio.plot(column=portfolio.wrapper.columns[0])
        
        # Save the plot
        print("Saving plot to HTML...")
        fig.write_html(str(report_path))
        
        # Verify the file exists
        if report_path.exists():
            size = report_path.stat().st_size
            print(f"Report saved successfully! File size: {size:,} bytes")
            print(f"Full path: {report_path.absolute()}")
        else:
            print("Warning: Report file was not created!")
            
    except Exception as e:
        print(f"\nError generating report: {str(e)}")
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()

def main():
    """Main entry point."""
    args = parse_args()
    
    # Download data
    data = download_data(args.symbols, args.start, args.end)
    if not data:
        print("Error: No data available for any symbols")
        return
    
    # Run backtest
    portfolio = run_backtest(data, args.strategy)
    
    # Generate report
    generate_report(portfolio)

if __name__ == '__main__':
    main() 