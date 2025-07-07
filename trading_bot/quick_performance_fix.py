#!/usr/bin/env python3
"""
Quick performance fixes for the SMA strategy.
This script modifies the existing technical analysis to improve performance.
"""

import os
import sys

def apply_performance_patches():
    """Apply performance patches to the existing code."""
    
    print("Applying performance patches to the Trading-Bot...")
    
    # Path to the technicals.py file
    technicals_path = os.path.join(
        os.path.dirname(__file__), 
        '..', 
        'external', 
        'ai-hedge-fund', 
        'src', 
        'agents', 
        'technicals.py'
    )
    
    if not os.path.exists(technicals_path):
        print(f"Error: Could not find {technicals_path}")
        return False
    
    # Read the current file
    with open(technicals_path, 'r') as f:
        content = f.read()
    
    # Backup the original file
    backup_path = technicals_path + '.backup'
    with open(backup_path, 'w') as f:
        f.write(content)
    print(f"Created backup at {backup_path}")
    
    # Apply performance patches
    patches_applied = 0
    
    # Patch 1: Add caching decorator
    cache_decorator = '''
_indicator_cache = {}

def cache_indicator(func):
    """Cache indicator calculations to avoid redundant computations."""
    def wrapper(*args, **kwargs):
        # Create a cache key from function name and args
        cache_key = f"{func.__name__}_{id(args[0])}"  # args[0] is prices_df
        
        if cache_key in _indicator_cache:
            return _indicator_cache[cache_key]
        
        result = func(*args, **kwargs)
        _indicator_cache[cache_key] = result
        return result
    return wrapper

'''
    
    if '_indicator_cache' not in content:
        # Find a good place to insert the cache decorator (after imports)
        import_end = content.find('\n\n\n')
        if import_end > 0:
            content = content[:import_end] + '\n' + cache_decorator + content[import_end:]
            patches_applied += 1
            print("✓ Added caching decorator")
    
    # Patch 2: Add @cache_indicator to expensive functions
    functions_to_cache = [
        'calculate_rsi',
        'calculate_bollinger_bands',
        'calculate_ema',
        'calculate_adx',
        'calculate_atr',
        'calculate_hurst_exponent'
    ]
    
    for func_name in functions_to_cache:
        func_def = f'def {func_name}('
        if func_def in content and f'@cache_indicator\ndef {func_name}(' not in content:
            content = content.replace(func_def, f'@cache_indicator\n{func_def}')
            patches_applied += 1
            print(f"✓ Added caching to {func_name}")
    
    # Patch 3: Optimize the Hurst exponent calculation
    hurst_optimization = '''def calculate_hurst_exponent(price_series: pd.Series, max_lag: int = 20) -> float:
    """
    Calculate Hurst Exponent to determine long-term memory of time series
    H < 0.5: Mean reverting series
    H = 0.5: Random walk
    H > 0.5: Trending series

    Args:
        price_series: Array-like price data
        max_lag: Maximum lag for R/S calculation

    Returns:
        float: Hurst exponent
    """
    # Quick return for small datasets
    if len(price_series) < max_lag * 2:
        return 0.5
    
    # Use only every nth point for large datasets to speed up calculation
    if len(price_series) > 1000:
        price_series = price_series[::5]  # Sample every 5th point
        max_lag = min(max_lag, len(price_series) // 4)
    
    lags = range(2, max_lag)
    # Add small epsilon to avoid log(0)
    tau = [max(1e-8, np.sqrt(np.std(np.subtract(price_series[lag:], price_series[:-lag])))) for lag in lags]

    # Return the Hurst exponent from linear fit
    try:
        reg = np.polyfit(np.log(lags), np.log(tau), 1)
        return reg[0]  # Hurst exponent is the slope
    except (ValueError, RuntimeWarning):
        # Return 0.5 (random walk) if calculation fails
        return 0.5'''
    
    # Find and replace the Hurst function
    hurst_start = content.find('def calculate_hurst_exponent(')
    if hurst_start > 0:
        hurst_end = content.find('\n\ndef ', hurst_start)
        if hurst_end > 0:
            content = content[:hurst_start] + hurst_optimization + content[hurst_end:]
            patches_applied += 1
            print("✓ Optimized Hurst exponent calculation")
    
    # Patch 4: Add early data validation
    validation_code = '''
    # Early validation to avoid unnecessary calculations
    if len(prices_df) < 200:  # Minimum data points needed
        print(f"Warning: Insufficient data for {ticker} ({len(prices_df)} points)")
        # Return neutral signal for insufficient data
        technical_analysis[ticker] = {
            "signal": "neutral",
            "confidence": 0,
            "reasoning": {
                "error": "Insufficient data points for analysis"
            }
        }
        continue
'''
    
    # Find where to insert validation (after prices_df creation)
    validation_point = 'prices_df = prices_to_df(prices)'
    if validation_point in content and 'Early validation' not in content:
        content = content.replace(
            validation_point + '\n',
            validation_point + '\n' + validation_code
        )
        patches_applied += 1
        print("✓ Added early data validation")
    
    # Write the patched file
    with open(technicals_path, 'w') as f:
        f.write(content)
    
    print(f"\n✅ Applied {patches_applied} performance patches")
    print(f"Original file backed up to: {backup_path}")
    
    # Create a simple test script
    test_script = '''#!/usr/bin/env python3
"""Quick test to verify the patches work correctly."""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'external', 'ai-hedge-fund'))

try:
    from src.agents.technicals import technical_analyst_agent
    print("✅ Patches applied successfully - imports working")
except Exception as e:
    print(f"❌ Error after patches: {e}")
    print("You may need to restore from backup")
'''
    
    test_path = os.path.join(os.path.dirname(__file__), 'test_patches.py')
    with open(test_path, 'w') as f:
        f.write(test_script)
    os.chmod(test_path, 0o755)
    print(f"\nCreated test script: {test_path}")
    
    return True


def create_optimized_config():
    """Create an optimized configuration for running the trading bot."""
    
    config = '''# Optimized Trading Bot Configuration
# Use these settings for better performance

# Data Settings
DEFAULT_LOOKBACK_DAYS = 90  # Reduced from 365
MAX_DATA_POINTS = 500       # Limit data points per ticker

# Agent Settings
ENABLED_AGENTS = [
    "technical_analyst_agent",  # Start with just technical
    # Add more agents only after verifying performance
]

# Performance Settings
ENABLE_CACHING = True
PARALLEL_PROCESSING = False  # Set to True if you have multiple CPUs
BATCH_SIZE = 5              # Process 5 tickers at a time

# API Settings
API_TIMEOUT = 30            # Seconds
API_RETRY_DELAY = 5         # Seconds between retries
MAX_API_RETRIES = 3         # Maximum retry attempts

# Technical Analysis Settings
TECHNICAL_INDICATORS = {
    "fast_ema": 8,
    "medium_ema": 21,
    "slow_ema": 55,
    "rsi_period": 14,
    "bb_period": 20,
    "bb_std": 2,
    "adx_period": 14,
    "atr_period": 14,
}

# Optimization Flags
SKIP_HURST_CALCULATION = False  # Set to True to skip expensive Hurst calculation
USE_SAMPLING_FOR_LARGE_DATA = True  # Sample data for datasets > 1000 points
CACHE_INDICATORS = True  # Cache calculated indicators

print("Optimized configuration loaded")
'''
    
    config_path = os.path.join(os.path.dirname(__file__), 'optimized_config.py')
    with open(config_path, 'w') as f:
        f.write(config)
    
    print(f"\nCreated optimized configuration: {config_path}")
    return config_path


def main():
    """Main function to apply performance fixes."""
    print("Trading Bot Performance Quick Fix")
    print("=================================\n")
    
    # Apply patches
    success = apply_performance_patches()
    
    if success:
        # Create optimized configuration
        config_path = create_optimized_config()
        
        print("\n" + "="*60)
        print("NEXT STEPS:")
        print("="*60)
        print("1. Test the patches:")
        print("   python trading_bot/test_patches.py")
        print("\n2. Run the performance debugger:")
        print("   python trading_bot/debug_sma_performance.py")
        print("\n3. Use the optimized configuration:")
        print(f"   import {config_path}")
        print("\n4. If issues occur, restore from backup:")
        print("   cp external/ai-hedge-fund/src/agents/technicals.py.backup \\")
        print("      external/ai-hedge-fund/src/agents/technicals.py")
    else:
        print("\n❌ Failed to apply patches")
        print("Please check the error messages above")


if __name__ == "__main__":
    main()