# strategies/example_strategy.py
from strategies.base_strategy import BaseStrategy
import pandas as pd
from typing import Optional, Dict, Any

class ExampleStrategy(BaseStrategy):
    """
    Example strategy implementation that demonstrates basic trading logic with position management.
    
    This strategy serves as a template for implementing new trading strategies. It includes:
    - Position checking before generating signals
    - Basic price-based signal generation
    - Proper documentation and type hints
    
    Attributes:
        threshold (float): Price change threshold for generating signals
    """
    
    def __init__(self, strategy_config: dict, common_config: dict | None = None):
        super().__init__(strategy_config=strategy_config, common_config=common_config)
        print(f"ExampleStrategy initialized with config: {strategy_config}")
        self.threshold = strategy_config.get('threshold', 0.1)

    def generate_signals(self, data: pd.DataFrame) -> str:
        """
        Generate trading signals based on price data and current positions.
        
        This method implements a simple price-based strategy that:
        1. Checks current position before generating buy signals
        2. Only generates sell signals if there's an existing position
        3. Uses a threshold-based approach for signal generation
        
        Args:
            data (pd.DataFrame): Price data with columns [open, high, low, close, volume]
                               and timestamp index
        
        Returns:
            str: 'buy', 'sell', or 'hold' signal
        
        Note:
            - Buy signals are only generated if no position exists
            - Sell signals are only generated if a position exists
            - Hold is returned if conditions aren't met or data is invalid
        """
        if data.empty:
            print("ExampleStrategy: No data to generate signals.")
            return "hold"

        # Ensure data has expected columns
        required_cols = ['open', 'close']
        if not all(col in data.columns for col in required_cols):
            print(f"ExampleStrategy: Data missing required columns ({required_cols}). Columns available: {data.columns}")
            return "hold"
            
        latest_close = data['close'].iloc[-1]
        latest_open = data['open'].iloc[-1]
        symbol = data.name if hasattr(data, 'name') else None

        print(f"ExampleStrategy ({self.strategy_config.get('name', 'Unnamed')}): Generating signal for data ending {data.index[-1]}. Open: {latest_open}, Close: {latest_close}, Threshold: {self.threshold}")
        
        # Check current position if broker is available
        current_position = 0
        if self.broker and symbol:
            try:
                current_position = self.broker.get_position(symbol)
            except Exception as e:
                print(f"Error checking position for {symbol}: {e}")
                return "hold"
        
        # Generate signals based on price movement and current position
        if latest_close > latest_open + self.threshold:
            # Only buy if we don't have a position
            return "hold" if current_position > 0 else "buy"
        elif latest_close < latest_open - self.threshold:
            # Only sell if we have a position
            return "sell" if current_position > 0 else "hold"
        else:
            return "hold"

    def execute_trades(self, signals, broker):
        """
        Execute trades based on generated signals.
        
        Note: This method is currently a placeholder as the main loop handles
        signal execution. It can be extended for more complex order management
        if needed.
        
        Args:
            signals: Trading signals
            broker: Broker interface for executing trades
        """
        print("ExampleStrategy: execute_trades called. This strategy relies on the main loop for simple signal execution.")
        pass 