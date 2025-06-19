import pandas as pd

class ExampleBacktestStrategy:
    """
    Simple SMA(50/200) crossover:
      • entry  = close > SMA50 AND SMA50 > SMA200
      • exit   = close < SMA50
    Returns a dict with 'entry' and 'exit' Series for vectorbt.
    """

    def __init__(self, fast=50, slow=200):
        self.fast = fast
        self.slow = slow

    def generate_signals(self, df: pd.DataFrame):
        close = df['Close']
        sma_fast = close.rolling(self.fast).mean()
        sma_slow = close.rolling(self.slow).mean()

        entry = (close > sma_fast) & (sma_fast > sma_slow)
        exit_ = close < sma_fast

        # vectorbt needs boolean Series indexed same as price
        return {'entry': entry, 'exit': exit_} 