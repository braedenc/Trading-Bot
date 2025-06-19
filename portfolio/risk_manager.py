import pandas as pd
from typing import Dict, Any

class RiskManager:
    """
    Manages position sizing and risk parameters for trading strategies.
    
    This class implements position sizing based on:
    - Account capital
    - Risk per trade percentage
    - Average True Range (ATR) for volatility
    - Stop loss and take profit percentages
    
    Attributes:
        risk_per_trade (float): Maximum risk per trade as a percentage of capital
        stop_loss_pct (float): Stop loss percentage from entry price
        take_profit_pct (float): Take profit percentage from entry price
    """
    
    def __init__(self, risk_config: Dict[str, Any]):
        """
        Initialize risk manager with configuration parameters.
        
        Args:
            risk_config (Dict[str, Any]): Risk configuration dictionary containing:
                - risk_per_trade: Percentage of capital to risk per trade (default: 0.01)
                - stop_loss_pct: Stop loss percentage (default: 0.02)
                - take_profit_pct: Take profit percentage (default: 0.05)
        """
        self.risk_per_trade = risk_config.get("risk_per_trade", 0.01)  # 1% default
        self.stop_loss_pct = risk_config.get("stop_loss_pct", 0.02)    # 2% default
        self.take_profit_pct = risk_config.get("take_profit_pct", 0.05)  # 5% default

    def position_size(self, capital: float, atr: float, price: float) -> int:
        """
        Calculate position size based on risk parameters and volatility.
        
        The calculation uses:
        1. Dollar risk per trade = capital * risk_per_trade
        2. Dollar risk per share = ATR * 2 (stop loss at 2*ATR)
        3. Position size = dollar risk per trade / dollar risk per share
        
        Args:
            capital (float): Available trading capital
            atr (float): Average True Range (volatility measure)
            price (float): Current price of the instrument
            
        Returns:
            int: Number of shares to trade, rounded down to nearest integer
            
        Example:
            >>> rm = RiskManager({"risk_per_trade": 0.01})
            >>> rm.position_size(capital=100000, atr=2.5, price=100)
            20  # Can risk $1000 (1% of $100k) with $5 risk per share (2*ATR)
        """
        dollar_risk_per_trade = capital * self.risk_per_trade
        dollar_risk_per_share = atr * 2
        if dollar_risk_per_share == 0:
            return 0
        qty = int(dollar_risk_per_trade / dollar_risk_per_share)
        return max(qty, 0) 