#!/usr/bin/env python3
"""
Live Trading Runner

Loads and executes trading strategies dynamically using the plugin loader system.
Supports both local strategies and external packages like ai-hedge-fund.
"""

import argparse
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
import logging

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from trading_bot.execution import StrategyExecutor, create_sample_config
from trading_bot.loader.plugin_loader import load_strategy, PluginLoaderError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_mock_market_data():
    """Generate mock market data for testing."""
    return {
        'prices': {
            'AAPL': {
                'current': 150.0,
                'high': 152.0,
                'low': 148.0,
                'volume': 1000000,
                'timestamp': datetime.now()
            },
            'GOOGL': {
                'current': 2800.0,
                'high': 2850.0,
                'low': 2750.0,
                'volume': 500000,
                'timestamp': datetime.now()
            }
        },
        'positions': {
            'AAPL': 0,
            'GOOGL': 0
        },
        'timestamp': datetime.now()
    }


async def run_live_trading(config_path: str, dry_run: bool = True):
    """
    Run live trading with strategies loaded from configuration.
    
    Args:
        config_path: Path to strategy configuration file
        dry_run: If True, run in simulation mode without real trades
    """
    logger.info(f"🚀 Starting live trading runner (dry_run={dry_run})")
    
    try:
        # Initialize strategy executor
        executor = StrategyExecutor(config_path)
        
        # Load strategies from configuration
        logger.info("📥 Loading strategies from configuration...")
        executor.load_strategies()
        
        # Display loaded strategies
        strategies = executor.get_strategy_status()
        logger.info(f"✅ Successfully loaded {len(strategies)} strategies:")
        
        for name, status in strategies.items():
            if status.get('is_active', False):
                logger.info(f"  ✅ {name}: {status.get('name', 'Unknown')}")
            else:
                logger.warning(f"  ⚠️  {name}: Inactive - {status.get('error', 'Unknown error')}")
        
        if not strategies:
            logger.error("❌ No strategies loaded. Please check configuration.")
            return False
        
        # Generate mock market data
        market_snapshot = generate_mock_market_data()
        logger.info("📊 Generated mock market data")
        
        # Execute strategies
        logger.info("🔄 Executing strategies...")
        results = await executor.execute_strategies(market_snapshot)
        
        # Display results
        logger.info("📈 Strategy execution results:")
        total_signals = 0
        
        for strategy_name, signals in results.items():
            signal_count = len(signals)
            total_signals += signal_count
            
            if signal_count > 0:
                logger.info(f"  📊 {strategy_name}: {signal_count} signals")
                for signal in signals[:3]:  # Show first 3 signals
                    logger.info(f"    • {signal.get('symbol')} {signal.get('action')} {signal.get('quantity', 0)}")
                if signal_count > 3:
                    logger.info(f"    ... and {signal_count - 3} more signals")
            else:
                logger.info(f"  📊 {strategy_name}: No signals generated")
        
        logger.info(f"🎯 Total signals generated: {total_signals}")
        
        # Cleanup
        await executor.shutdown()
        logger.info("✅ Live trading session completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Live trading failed: {e}")
        return False


def test_bad_path_error():
    """Test that bad paths raise clean errors."""
    logger.info("🧪 Testing error handling for bad paths...")
    
    test_cases = [
        "nonexistent.module:BadClass",
        "trading_bot.agents.sma_agent:NonExistentClass", 
        "invalid_format_no_colon",
        "badmodule:NoClass"
    ]
    
    for bad_path in test_cases:
        try:
            load_strategy(bad_path)
            logger.error(f"❌ Bad path '{bad_path}' should have failed but didn't!")
            return False
        except PluginLoaderError as e:
            logger.info(f"✅ Bad path '{bad_path}' correctly raised: {str(e)[:100]}...")
        except Exception as e:
            logger.error(f"❌ Bad path '{bad_path}' raised unexpected error: {e}")
            return False
    
    logger.info("✅ All bad path tests passed")
    return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Live Trading Runner")
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Run in dry-run mode (simulation only)"
    )
    parser.add_argument(
        "--config", 
        default="config.yaml",
        help="Path to strategy configuration file"
    )
    parser.add_argument(
        "--create-config",
        action="store_true",
        help="Create a sample configuration file and exit"
    )
    parser.add_argument(
        "--test-errors",
        action="store_true", 
        help="Test error handling and exit"
    )
    
    args = parser.parse_args()
    
    # Create sample config if requested
    if args.create_config:
        create_sample_config(args.config)
        logger.info(f"✅ Sample configuration created: {args.config}")
        return
    
    # Test error handling if requested
    if args.test_errors:
        success = test_bad_path_error()
        sys.exit(0 if success else 1)
    
    # Check if config file exists
    if not os.path.exists(args.config):
        logger.error(f"❌ Configuration file not found: {args.config}")
        logger.info(f"💡 Create one with: {sys.argv[0]} --create-config")
        sys.exit(1)
    
    # Run live trading
    try:
        success = asyncio.run(run_live_trading(args.config, args.dry_run))
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("👋 Live trading interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()