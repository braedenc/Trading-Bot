"""
Trading Bot Execution Engine

Loads and executes trading strategies using the plugin loader system.
Supports dynamic strategy loading from configuration files.
"""

import asyncio
import logging
import yaml
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from .loader.plugin_loader import load_strategy, PluginLoaderError
from .base_agent import BaseAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StrategyExecutionError(Exception):
    """Exception raised during strategy execution."""
    pass


class StrategyExecutor:
    """
    Executes trading strategies loaded via plugin loader.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the strategy executor.
        
        Args:
            config_path: Path to configuration file (default: config.yaml)
        """
        self.config_path = config_path or "config.yaml"
        self.strategies: Dict[str, BaseAgent] = {}
        self.config: Dict[str, Any] = {}
        self.is_running = False
        
    def load_config(self) -> None:
        """Load configuration from YAML file."""
        try:
            config_file = Path(self.config_path)
            if not config_file.exists():
                raise StrategyExecutionError(f"Configuration file not found: {self.config_path}")
            
            with open(config_file, 'r') as f:
                self.config = yaml.safe_load(f)
            
            logger.info(f"Loaded configuration from {self.config_path}")
            
        except yaml.YAMLError as e:
            raise StrategyExecutionError(f"Invalid YAML in {self.config_path}: {e}")
        except Exception as e:
            raise StrategyExecutionError(f"Failed to load config {self.config_path}: {e}")
    
    def load_strategies(self) -> None:
        """Load all strategies from configuration."""
        if not self.config:
            self.load_config()
        
        strategies_config = self.config.get('strategies', [])
        if not strategies_config:
            raise StrategyExecutionError("No strategies defined in configuration")
        
        logger.info(f"Loading {len(strategies_config)} strategies...")
        
        for strategy_config in strategies_config:
            try:
                self._load_single_strategy(strategy_config)
            except Exception as e:
                logger.error(f"Failed to load strategy {strategy_config.get('name', 'unknown')}: {e}")
                # Continue loading other strategies
        
        if not self.strategies:
            raise StrategyExecutionError("No strategies loaded successfully")
        
        logger.info(f"Successfully loaded {len(self.strategies)} strategies")
    
    def _load_single_strategy(self, strategy_config: Dict[str, Any]) -> None:
        """
        Load a single strategy from configuration.
        
        Args:
            strategy_config: Strategy configuration dict
        """
        name = strategy_config.get('name')
        path = strategy_config.get('path')
        params = strategy_config.get('params', {})
        
        if not name:
            raise StrategyExecutionError("Strategy missing 'name' field")
        if not path:
            raise StrategyExecutionError(f"Strategy '{name}' missing 'path' field")
        
        logger.info(f"Loading strategy '{name}' from path '{path}'")
        
        # Load the strategy class
        strategy_class = load_strategy(path)
        
        # Verify it inherits from BaseAgent
        if not issubclass(strategy_class, BaseAgent):
            raise StrategyExecutionError(
                f"Strategy class {strategy_class.__name__} must inherit from BaseAgent"
            )
        
        # Create instance with parameters
        try:
            if params:
                strategy_instance = strategy_class(name=name, **params)
            else:
                strategy_instance = strategy_class(name=name)
        except TypeError as e:
            # Try without name parameter for backwards compatibility
            try:
                if params:
                    strategy_instance = strategy_class(**params)
                else:
                    strategy_instance = strategy_class(name)
                # Set name manually if the instance supports it
                if hasattr(strategy_instance, 'name'):
                    strategy_instance.name = name
            except Exception:
                raise StrategyExecutionError(f"Failed to create strategy '{name}': {e}")
        
        self.strategies[name] = strategy_instance
        logger.info(f"Successfully loaded strategy '{name}'")
    
    async def execute_strategies(self, market_snapshot: Dict[str, Any]) -> Dict[str, List[Dict]]:
        """
        Execute all loaded strategies with market data.
        
        Args:
            market_snapshot: Market data snapshot
            
        Returns:
            Dict mapping strategy names to their generated signals
        """
        if not self.strategies:
            raise StrategyExecutionError("No strategies loaded")
        
        results = {}
        
        # Execute strategies concurrently
        tasks = []
        for name, strategy in self.strategies.items():
            task = asyncio.create_task(
                self._execute_single_strategy(name, strategy, market_snapshot)
            )
            tasks.append((name, task))
        
        # Wait for all strategies to complete
        for name, task in tasks:
            try:
                signals = await task
                results[name] = signals
                logger.debug(f"Strategy '{name}' generated {len(signals)} signals")
            except Exception as e:
                logger.error(f"Strategy '{name}' execution failed: {e}")
                results[name] = []  # Empty signals on failure
        
        return results
    
    async def _execute_single_strategy(
        self, 
        name: str, 
        strategy: BaseAgent, 
        market_snapshot: Dict[str, Any]
    ) -> List[Dict]:
        """
        Execute a single strategy.
        
        Args:
            name: Strategy name
            strategy: Strategy instance
            market_snapshot: Market data snapshot
            
        Returns:
            List of signals generated by the strategy
        """
        try:
            if not strategy.is_active:
                logger.warning(f"Strategy '{name}' is inactive, skipping")
                return []
            
            signals = await strategy.generate_signals(market_snapshot)
            
            # Validate signals format
            if not isinstance(signals, list):
                logger.error(f"Strategy '{name}' returned invalid signals format (not a list)")
                return []
            
            # Add strategy metadata to each signal
            for signal in signals:
                if isinstance(signal, dict):
                    signal['strategy'] = name
                    signal['timestamp'] = datetime.now().isoformat()
            
            return signals
            
        except Exception as e:
            logger.error(f"Error executing strategy '{name}': {e}")
            return []
    
    async def notify_fills(self, fills: List[Dict[str, Any]]) -> None:
        """
        Notify all strategies of order fills.
        
        Args:
            fills: List of fill notifications
        """
        if not fills:
            return
        
        tasks = []
        for name, strategy in self.strategies.items():
            for fill in fills:
                task = asyncio.create_task(
                    self._notify_single_strategy_fill(name, strategy, fill)
                )
                tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _notify_single_strategy_fill(
        self, 
        name: str, 
        strategy: BaseAgent, 
        fill: Dict[str, Any]
    ) -> None:
        """Notify a single strategy of a fill."""
        try:
            await strategy.on_fill(fill)
        except Exception as e:
            logger.error(f"Error notifying strategy '{name}' of fill: {e}")
    
    async def update_risk_limits(self, limits: Dict[str, Any]) -> None:
        """
        Update risk limits for all strategies.
        
        Args:
            limits: New risk limits
        """
        tasks = []
        for name, strategy in self.strategies.items():
            task = asyncio.create_task(
                self._update_single_strategy_limits(name, strategy, limits)
            )
            tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _update_single_strategy_limits(
        self, 
        name: str, 
        strategy: BaseAgent, 
        limits: Dict[str, Any]
    ) -> None:
        """Update risk limits for a single strategy."""
        try:
            await strategy.on_limit_update(limits)
            strategy.set_risk_limits(limits)
        except Exception as e:
            logger.error(f"Error updating limits for strategy '{name}': {e}")
    
    def get_strategy_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all loaded strategies."""
        status = {}
        for name, strategy in self.strategies.items():
            try:
                status[name] = strategy.get_status()
            except Exception as e:
                status[name] = {
                    'name': name,
                    'error': str(e),
                    'is_active': False
                }
        return status
    
    async def shutdown(self) -> None:
        """Gracefully shutdown all strategies."""
        logger.info("Shutting down strategy executor...")
        
        tasks = []
        for name, strategy in self.strategies.items():
            task = asyncio.create_task(strategy.shutdown())
            tasks.append((name, task))
        
        # Wait for all strategies to shutdown
        for name, task in tasks:
            try:
                await task
                logger.debug(f"Strategy '{name}' shutdown complete")
            except Exception as e:
                logger.error(f"Error shutting down strategy '{name}': {e}")
        
        self.strategies.clear()
        self.is_running = False
        logger.info("Strategy executor shutdown complete")


# Convenience functions for common usage patterns
async def run_single_strategy(
    strategy_path: str, 
    market_snapshot: Dict[str, Any],
    params: Optional[Dict[str, Any]] = None
) -> List[Dict]:
    """
    Run a single strategy without configuration file.
    
    Args:
        strategy_path: Path to strategy class
        market_snapshot: Market data snapshot
        params: Optional parameters for strategy initialization
        
    Returns:
        List of signals generated by the strategy
    """
    try:
        strategy_class = load_strategy(strategy_path)
        
        # Create instance
        if params:
            strategy = strategy_class(**params)
        else:
            strategy = strategy_class()
        
        # Execute
        signals = await strategy.generate_signals(market_snapshot)
        
        # Cleanup
        await strategy.shutdown()
        
        return signals
        
    except Exception as e:
        logger.error(f"Failed to run strategy {strategy_path}: {e}")
        return []


def create_sample_config(output_path: str = "config.yaml") -> None:
    """
    Create a sample configuration file.
    
    Args:
        output_path: Where to save the sample config
    """
    sample_config = {
        'strategies': [
            {
                'name': 'SMA_Cross',
                'path': 'trading_bot.agents.sma_agent:SMAAgent',
                'params': {
                    'fast_period': 10,
                    'slow_period': 20
                }
            },
            {
                'name': 'Technical_Analysis',
                'path': 'trading_bot.agents.optimized_technicals:OptimizedTechnicalAgent',
                'params': {}
            },
            {
                'name': 'AI_Hedge_Fund',
                'path': 'external.ai_hedge_fund.strategies.momentum:MomentumStrategy',
                'params': {
                    'lookback_period': 30,
                    'threshold': 0.02
                }
            }
        ],
        'execution': {
            'max_concurrent_strategies': 10,
            'timeout_seconds': 30
        },
        'risk_limits': {
            'max_position_size': 1000000,
            'max_daily_loss': 50000,
            'max_leverage': 3.0,
            'allowed_symbols': ['AAPL', 'GOOGL', 'MSFT', 'TSLA']
        }
    }
    
    with open(output_path, 'w') as f:
        yaml.dump(sample_config, f, default_flow_style=False, sort_keys=False)
    
    logger.info(f"Sample configuration saved to {output_path}")