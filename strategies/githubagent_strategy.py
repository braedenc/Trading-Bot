import pandas as pd
from importlib import import_module

# -------- load original decision function --------
decide_fn = getattr(
    import_module("ai_hedge_fund.src.trader"),  # adjust only if path differs
    "agent_decide"
)

class GithubAgentStrategy:
    """
    Adapter for ai-hedge-fund 'agent_decide'.
    • mode='live'  -> returns 'buy'/'sell'/'hold'
    • mode='bt'    -> returns {'entry': Series, 'exit': Series}
    """

    def __init__(self, strategy_config=None, common_config=None):
        cfg = strategy_config or {}
        self.mode = cfg.get("mode", "live").lower()

    # ------------------------------------------------
    def generate_signals(self, df: pd.DataFrame):
        symbol = df.name.upper()          # tag set by main.py
        closes = df["Close"]

        if self.mode == "live":
            decision = decide_fn(symbol, closes.iloc[-1]).lower()
            return decision  # 'buy' | 'sell' | 'hold'

        # back-test mode: evaluate every bar
        decisions = closes.apply(lambda c: decide_fn(symbol, c).lower())
        entry = decisions == "buy"
        exit_ = decisions == "sell"
        return {"entry": entry, "exit": exit_}

    # optional so ExampleStrategy-style broker calls work
    def set_broker(self, broker):
        self.broker = broker 