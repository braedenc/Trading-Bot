"""
Simple Moving Average (SMA) Trading Agent
High-performance implementation with optimized calculations.
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

# Try to import pandas/numpy for optimized performance
try:
    import numpy as np
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

from trading_bot.base_agent import BaseAgent


class SMAAgent(BaseAgent):
    """
    Simple Moving Average trading agent with crossover strategy.
    
    Strategy:
    - Buy when fast SMA crosses above slow SMA
    - Sell when fast SMA crosses below slow SMA
    - Uses optimized pandas operations for performance
    """
    
    def __init__(self, 
                 fast_period: int = 10, 
                 slow_period: int = 20,
                 min_data_points: int = 50,
                 position_size_pct: float = 0.1):
        """
        Initialize SMA agent.
        
        Args:
            fast_period: Period for fast SMA
            slow_period: Period for slow SMA  
            min_data_points: Minimum data points needed for signals
            position_size_pct: Position size as percentage of portfolio
        """
        super().__init__("SMA_Agent")
        
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.min_data_points = min_data_points
        self.position_size_pct = position_size_pct
        
        # Performance optimization: cache calculations
        self._price_cache = {}
        self._sma_cache = {}
        self._last_signals = {}
        
        # Logging
        self.logger = logging.getLogger(f"trading_bot.{self.name}")
        
    async def generate_signals(self, snapshot: dict) -> List[dict]:
        """
        Generate SMA crossover signals.
        
        Performance optimizations:
        1. Cache price data and SMA calculations
        2. Use vectorized pandas operations
        3. Only recalculate when new data arrives
        4. Early exit for insufficient data
        """
        signals = []
        
        try:
            prices_data = snapshot.get('prices', {})
            current_positions = snapshot.get('positions', {})
            
            for symbol, price_data in prices_data.items():
                signal = await self._generate_signal_for_symbol(
                    symbol, price_data, current_positions.get(symbol, 0)
                )
                
                if signal:
                    signals.append(signal)
                    
        except Exception as e:
            self.logger.error(f"Error generating signals: {e}")
            
        return signals
    
    async def _generate_signal_for_symbol(self, symbol: str, price_data: dict, current_position: float) -> dict:
        """Generate signal for a single symbol with performance optimizations."""
        
        # Extract price series
        if 'historical' not in price_data or len(price_data['historical']) < self.min_data_points:
            return None
            
        # Convert to appropriate data structure
        data = self._create_price_dataframe(price_data['historical'])
        
        if HAS_PANDAS and hasattr(data, 'iloc'):
            # Pandas path
            if len(data) < max(self.fast_period, self.slow_period):
                return None
                
            cache_key = f"{symbol}_{len(data)}_{data['close'].iloc[-1]}"
            if cache_key in self._sma_cache:
                fast_sma, slow_sma = self._sma_cache[cache_key]
            else:
                fast_sma = data['close'].rolling(window=self.fast_period, min_periods=self.fast_period).mean()
                slow_sma = data['close'].rolling(window=self.slow_period, min_periods=self.slow_period).mean()
                self._sma_cache[cache_key] = (fast_sma, slow_sma)
                
            current_fast = fast_sma.iloc[-1]
            current_slow = slow_sma.iloc[-1]
            prev_fast = fast_sma.iloc[-2] if len(fast_sma) > 1 else current_fast
            prev_slow = slow_sma.iloc[-2] if len(slow_sma) > 1 else current_slow
            current_price = data['close'].iloc[-1]
        else:
            # Simple list path
            if len(data) < max(self.fast_period, self.slow_period):
                return None
                
            # Calculate SMAs using simple method
            current_fast = self._simple_sma(data, self.fast_period)
            current_slow = self._simple_sma(data, self.slow_period)
            prev_fast = self._simple_sma(data[:-1], self.fast_period) if len(data) > self.fast_period else current_fast
            prev_slow = self._simple_sma(data[:-1], self.slow_period) if len(data) > self.slow_period else current_slow
            current_price = data[-1]
            
            if current_fast is None or current_slow is None:
                return None
        
        # Detect crossovers
        signal = self._detect_crossover(
            current_fast, current_slow, prev_fast, prev_slow, 
            current_position, symbol, current_price
        )
        
        return signal
    
    def _simple_sma(self, prices: List[float], period: int) -> float:
        """Simple moving average calculation without numpy."""
        if len(prices) < period:
            return None
        return sum(prices[-period:]) / period
    
    def _create_price_dataframe(self, historical_data: List[dict]):
        """Convert historical price data to DataFrame or simple list based on availability."""
        
        if HAS_PANDAS:
            # Use pandas for optimized performance
            data = [
                {
                    'timestamp': item['timestamp'],
                    'close': float(item['close']),
                    'volume': float(item.get('volume', 0))
                }
                for item in historical_data
            ]
            
            df = pd.DataFrame(data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp').reset_index(drop=True)
            return df
        else:
            # Simple fallback without pandas
            return [float(item['close']) for item in historical_data]
    
    def _detect_crossover(self, current_fast: float, current_slow: float, 
                         prev_fast: float, prev_slow: float,
                         current_position: float, symbol: str, current_price: float) -> dict:
        """Detect SMA crossover and generate appropriate signal."""
        
        # Bullish crossover: fast SMA crosses above slow SMA
        bullish_crossover = (prev_fast <= prev_slow) and (current_fast > current_slow)
        
        # Bearish crossover: fast SMA crosses below slow SMA  
        bearish_crossover = (prev_fast >= prev_slow) and (current_fast < current_slow)
        
        # Calculate position size based on risk limits
        max_position = self.risk_limits.get('max_position_size', 10000)
        target_position_size = min(max_position * self.position_size_pct, max_position)
        
        signal = None
        
        if bullish_crossover and current_position <= 0:
            # Buy signal
            quantity = target_position_size - current_position
            confidence = self._calculate_confidence(current_fast, current_slow, 'buy')
            
            signal = {
                'symbol': symbol,
                'action': 'buy',
                'quantity': quantity,
                'confidence': confidence,
                'reasoning': f'Fast SMA ({current_fast:.2f}) crossed above Slow SMA ({current_slow:.2f})',
                'metadata': {
                    'fast_sma': current_fast,
                    'slow_sma': current_slow,
                    'current_price': current_price,
                    'strategy': 'sma_crossover'
                }
            }
            
        elif bearish_crossover and current_position > 0:
            # Sell signal
            quantity = current_position  # Close entire position
            confidence = self._calculate_confidence(current_fast, current_slow, 'sell')
            
            signal = {
                'symbol': symbol,
                'action': 'sell',
                'quantity': quantity,
                'confidence': confidence,
                'reasoning': f'Fast SMA ({current_fast:.2f}) crossed below Slow SMA ({current_slow:.2f})',
                'metadata': {
                    'fast_sma': current_fast,
                    'slow_sma': current_slow,
                    'current_price': current_price,
                    'strategy': 'sma_crossover'
                }
            }
        
        return signal
    
    def _calculate_confidence(self, fast_sma: float, slow_sma: float, action: str) -> float:
        """Calculate confidence score based on SMA separation."""
        
        if fast_sma == 0 or slow_sma == 0:
            return 0.5
            
        # Calculate percentage difference between SMAs
        sma_diff_pct = abs(fast_sma - slow_sma) / slow_sma
        
        # Higher confidence for larger separations (up to 5%)
        confidence = min(0.5 + (sma_diff_pct * 10), 1.0)
        
        return confidence
    
    async def on_fill(self, fill: dict) -> None:
        """Handle order fill notifications."""
        symbol = fill.get('symbol')
        side = fill.get('side')
        quantity = fill.get('quantity', 0)
        price = fill.get('price', 0)
        
        self.logger.info(
            f"Fill received: {side} {quantity} {symbol} @ {price}"
        )
        
        # Update internal tracking if needed
        # This is where you might update position tracking, P&L calculation, etc.
        
    async def on_limit_update(self, limits: dict) -> None:
        """Handle risk limit updates."""
        self.set_risk_limits(limits)
        
        self.logger.info(f"Risk limits updated: {limits}")
        
        # Adjust position sizing if needed
        if 'max_position_size' in limits:
            # Could trigger position size adjustments here
            pass
    
    def get_performance_stats(self) -> dict:
        """Get performance statistics for the agent."""
        return {
            'name': self.name,
            'fast_period': self.fast_period,
            'slow_period': self.slow_period,
            'cache_size': len(self._sma_cache),
            'min_data_points': self.min_data_points,
            'position_size_pct': self.position_size_pct
        }
    
    async def shutdown(self) -> None:
        """Cleanup when shutting down."""
        await super().shutdown()
        
        # Clear caches
        self._price_cache.clear()
        self._sma_cache.clear()
        self._last_signals.clear()
        
        self.logger.info(f"{self.name} shutdown complete")


# Factory function for easy instantiation
def create_sma_agent(fast_period: int = 10, slow_period: int = 20, **kwargs) -> SMAAgent:
    """Create an SMA agent with specified parameters."""
    return SMAAgent(fast_period=fast_period, slow_period=slow_period, **kwargs)