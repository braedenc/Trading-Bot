"""
Base Agent class for the Trading Bot engine.
All trading agents must inherit from this class.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any
import asyncio
import logging
import sys
import os

# Add tools to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from tools import notify_fill, register_heartbeat_source, send_heartbeat, deregister_heartbeat_source
except ImportError:
    # Fallback if tools not available
    async def notify_fill(fill): return {'slack': False, 'email': False}
    async def register_heartbeat_source(name): pass
    async def send_heartbeat(name): pass
    async def deregister_heartbeat_source(name): pass


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
        self.logger = logging.getLogger(f"{self.__class__.__name__}({name})")
        self._heartbeat_registered = False
        
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
    
    async def _ensure_heartbeat_registered(self) -> None:
        """Ensure heartbeat is registered for this agent."""
        if not self._heartbeat_registered:
            try:
                await register_heartbeat_source(self.name)
                self._heartbeat_registered = True
            except Exception as e:
                self.logger.warning(f"Failed to register heartbeat: {e}")
    
    async def _send_heartbeat(self) -> None:
        """Send heartbeat signal."""
        try:
            await self._ensure_heartbeat_registered()
            await send_heartbeat(self.name)
        except Exception as e:
            self.logger.warning(f"Failed to send heartbeat: {e}")
    
    async def _notify_fill(self, fill: dict) -> None:
        """Send fill notification."""
        try:
            result = await notify_fill(fill)
            if result.get('slack') or result.get('email'):
                self.logger.info(f"Fill notification sent: {result}")
        except Exception as e:
            self.logger.warning(f"Failed to send fill notification: {e}")

    async def shutdown(self) -> None:
        """Gracefully shutdown the agent."""
        self.is_active = False
        
        # Deregister heartbeat
        if self._heartbeat_registered:
            try:
                await deregister_heartbeat_source(self.name)
                self._heartbeat_registered = False
            except Exception as e:
                self.logger.warning(f"Failed to deregister heartbeat: {e}")
        
        # Override in subclasses for cleanup
        pass