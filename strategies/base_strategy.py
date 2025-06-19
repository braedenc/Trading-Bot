from abc import ABC, abstractmethod
import pandas as pd

class BaseStrategy(ABC):
    """Abstract base class all strategies must inherit from."""

    def __init__(self, strategy_config: dict, common_config: dict | None = None):
        self.strategy_config = strategy_config
        self.common_config = common_config or {}

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> str:
        """Return 'buy', 'sell', or 'hold' for the given price data."""
        ...

    def set_broker(self, broker):
        """Optional: strategy can query broker positions."""
        self.broker = broker

    @abstractmethod
    def execute_trades(self, signals, broker):
        """Executes trades based on generated signals using the broker."""
        pass

    # Optional: Placeholder for LLM/GPT agent integration
    def get_agent_decision(self, market_context):
        """Optional method for strategies that use an AI agent."""
        # This can be overridden by strategies that leverage LLMs
        print("BaseStrategy: No AI agent decision implemented.")
        return None 