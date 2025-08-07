# Trading Bot Agents Package
"""
This package contains all trading agents for the Trading Bot.
"""

# Import core agents that work without numpy
try:
    from .sma_agent import SMAAgent, create_sma_agent
    __all__ = ['SMAAgent', 'create_sma_agent']
except ImportError as e:
    print(f"Warning: Could not import SMAAgent: {e}")
    __all__ = []

# Import optional agents that require additional dependencies
try:
    from .optimized_technicals import OptimizedTechnicalAgent
    __all__.append('OptimizedTechnicalAgent')
except ImportError:
    pass