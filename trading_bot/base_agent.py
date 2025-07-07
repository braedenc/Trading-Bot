"""
Base Agent class for the Trading Bot engine.
All trading agents must inherit from this class.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any
import asyncio


class BaseAgent(ABC):
    """
    Base class for all trading agents.
    
    As specified in the PRD:
    - Agent never calls broker or DB directly
    - Engine handles data ingest, risk caps, order routing
    - Agent only handles signal/sizing logic and model training
    """
    
    def __init__(self, name: str):
        self.name = name
        self.is_active = True
        self.risk_limits = {}
        
    @abstractmethod
    async def generate_signals(self, snapshot: dict) -> List[dict]:
        """
        Generate trading signals based on market data snapshot.
        
        Args:
            snapshot: Market data snapshot containing:
                - prices: Current and historical price data
                - positions: Current positions
                - risk_limits: Current risk limits
                - tick_data: Recent tick data from TickStore
        
        Returns:
            List of signal dictionaries with format:
            {
                'symbol': str,
                'action': 'buy'|'sell'|'hold',
                'quantity': float,
                'confidence': float,  # 0.0 to 1.0
                'reasoning': str,
                'metadata': dict
            }
        """
        pass
    
    @abstractmethod
    async def on_fill(self, fill: dict) -> None:
        """
        Handle order fill notifications.
        
        Args:
            fill: Fill information containing:
                - symbol: str
                - side: 'buy'|'sell'
                - quantity: float
                - price: float
                - timestamp: datetime
                - order_id: str
        """
        pass
    
    @abstractmethod
    async def on_limit_update(self, limits: dict) -> None:
        """
        Handle risk limit updates from the engine.
        
        Args:
            limits: Updated risk limits containing:
                - max_position_size: float
                - max_daily_loss: float
                - max_leverage: float
                - allowed_symbols: List[str]
        """
        pass
    
    def set_risk_limits(self, limits: dict) -> None:
        """Update agent's risk limits."""
        self.risk_limits = limits
    
    def get_status(self) -> dict:
        """Get agent status information."""
        return {
            'name': self.name,
            'is_active': self.is_active,
            'risk_limits': self.risk_limits
        }
    
    async def shutdown(self) -> None:
        """Gracefully shutdown the agent."""
        self.is_active = False
        # Override in subclasses for cleanup
        pass