"""
GitHub Agent wrapper for external strategies.
This wraps the ai-hedge-fund submodule as a trading agent.
"""

import asyncio
import sys
import os
from typing import List, Dict, Any
import logging

# Add the ai-hedge-fund to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'external', 'ai-hedge-fund'))

from trading_bot.base_agent import BaseAgent


class GitHubAgent(BaseAgent):
    """
    Wrapper for external GitHub-based trading strategies.
    Currently wraps the ai-hedge-fund strategy.
    """
    
    def __init__(self, strategy_name: str = "ai_hedge_fund"):
        """
        Initialize GitHub agent wrapper.
        
        Args:
            strategy_name: Name of the strategy to wrap
        """
        super().__init__(f"GitHub_{strategy_name}")
        
        self.strategy_name = strategy_name
        self.logger = logging.getLogger(f"trading_bot.{self.name}")
        
        # Import the external strategy
        try:
            from src.main import run_hedge_fund
            self.external_strategy = run_hedge_fund
            self.is_available = True
            self.logger.info(f"Successfully loaded {strategy_name}")
        except ImportError as e:
            self.logger.error(f"Failed to import {strategy_name}: {e}")
            self.external_strategy = None
            self.is_available = False
    
    async def generate_signals(self, snapshot: dict) -> List[dict]:
        """
        Generate signals by calling the external ai-hedge-fund strategy.
        """
        if not self.is_available:
            self.logger.warning("External strategy not available")
            return []
        
        signals = []
        
        try:
            # Extract data from snapshot
            prices_data = snapshot.get('prices', {})
            positions = snapshot.get('positions', {})
            
            # Convert to format expected by ai-hedge-fund
            tickers = list(prices_data.keys())
            
            if not tickers:
                return []
            
            # Create portfolio format for ai-hedge-fund
            portfolio = {
                "cash": 100000.0,  # Default cash amount
                "margin_requirement": 0.0,
                "margin_used": 0.0,
                "positions": {
                    ticker: {
                        "long": max(0, positions.get(ticker, 0)),
                        "short": max(0, -positions.get(ticker, 0)),
                        "long_cost_basis": 0.0,
                        "short_cost_basis": 0.0,
                        "short_margin_used": 0.0,
                    }
                    for ticker in tickers
                },
                "realized_gains": {
                    ticker: {"long": 0.0, "short": 0.0}
                    for ticker in tickers
                },
            }
            
            # Use recent date range (last 90 days)
            from datetime import datetime, timedelta
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
            
            # Call the external strategy
            result = await asyncio.to_thread(
                self.external_strategy,
                tickers=tickers,
                start_date=start_date,
                end_date=end_date,
                portfolio=portfolio,
                show_reasoning=False,
                selected_analysts=["technical_analyst_agent"],  # Use only technical for speed
                model_name="gpt-4o-mini",  # Use faster model
                model_provider="OpenAI"
            )
            
            # Convert ai-hedge-fund decisions to our signal format
            decisions = result.get("decisions", {})
            
            for ticker, decision in decisions.items():
                action = decision.get("action", "hold")
                quantity = decision.get("quantity", 0)
                reasoning = decision.get("reasoning", "AI hedge fund decision")
                
                if action != "hold" and quantity > 0:
                    signal = {
                        'symbol': ticker,
                        'action': action,
                        'quantity': quantity,
                        'confidence': 0.7,  # Default confidence
                        'reasoning': reasoning,
                        'metadata': {
                            'strategy': 'ai_hedge_fund',
                            'external_decision': decision,
                            'analyst_signals': result.get("analyst_signals", {})
                        }
                    }
                    signals.append(signal)
                    
        except Exception as e:
            self.logger.error(f"Error calling external strategy: {e}")
            # Don't fail completely, just return empty signals
            
        return signals
    
    async def on_fill(self, fill: dict) -> None:
        """Handle order fill notifications."""
        self.logger.info(f"GitHub agent received fill: {fill}")
        # The external strategy doesn't need to know about fills
        # as it operates on a different paradigm
    
    async def on_limit_update(self, limits: dict) -> None:
        """Handle risk limit updates."""
        self.set_risk_limits(limits)
        self.logger.info(f"GitHub agent risk limits updated: {limits}")
    
    def get_performance_stats(self) -> dict:
        """Get performance statistics."""
        return {
            'name': self.name,
            'strategy_name': self.strategy_name,
            'is_available': self.is_available,
            'external_strategy_loaded': self.external_strategy is not None
        }
    
    async def shutdown(self) -> None:
        """Cleanup when shutting down."""
        await super().shutdown()
        self.logger.info(f"{self.name} shutdown complete")


# Factory function for easy instantiation
def create_github_agent(strategy_name: str = "ai_hedge_fund") -> GitHubAgent:
    """Create a GitHub agent wrapper."""
    return GitHubAgent(strategy_name=strategy_name)