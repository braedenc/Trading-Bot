from ib_insync import IB, Stock, Forex, MarketOrder
import logging, time

class IBKRBroker:
    def __init__(self, config: dict, api_keys: dict = None):
        self.config = config
        self.host       = config.get("host", "127.0.0.1")
        self.port       = config.get("port", 7497)
        self.client_id  = config.get("client_id", 1)
        self.paper      = config.get("paper_trading", True)
        self.ib: IB | None = None

    # ---------- connection ----------
    def connect(self):
        self.ib = IB()
        try:
            self.ib.connect(self.host, self.port, clientId=self.client_id, timeout=5)
            logging.info("IBKRBroker connected (client_id=%s, paper=%s)", self.client_id, self.paper)
        except Exception as e:
            logging.error("IBKR connect failed: %s", e, exc_info=True)
            raise

    def disconnect(self):
        if self.ib and self.ib.isConnected():
            self.ib.disconnect()
            logging.info("IBKRBroker disconnected")

    # ---------- helpers ----------
    def _contract(self, symbol: str):
        if "/" in symbol:              # rudimentary FX test (e.g., EUR/USD)
            base, quote = symbol.split("/")
            return Forex(base + quote)
        return Stock(symbol, "SMART", "USD")

    def _place_order(self, action: str, symbol: str, quantity: int):
        if quantity <= 0:
            logging.warning("Quantity <=0 — order skipped")
            return None
        contract = self._contract(symbol)
        order    = MarketOrder(action.upper(), quantity)
        trade    = self.ib.placeOrder(contract, order)
        self.ib.sleep(0.2)             # allow status callback
        logging.info("Placed %s %s x%s (orderId=%s)",
                     action.upper(), symbol, quantity, trade.order.orderId)
        return trade

    # ---------- public API ----------
    def buy(self, symbol: str, quantity: int):
        return self._place_order("BUY", symbol, quantity)

    def sell(self, symbol: str, quantity: int):
        return self._place_order("SELL", symbol, quantity)

    def get_position(self, symbol: str) -> int:
        if not self.ib.isConnected():
            return 0
        for p in self.ib.positions():
            if p.contract.symbol.upper() == symbol.upper():
                return int(p.position)
        return 0

    def execute_signal(self, symbol: str, signal: str, quantity: int = 1):
        """
        Execute a trading signal (BUY/SELL) for a symbol.
        
        Args:
            symbol (str): The trading symbol
            signal (str): The signal to execute ('BUY' or 'SELL')
            quantity (int, optional): The quantity to trade. Defaults to 1.
        """
        if signal.upper() == "BUY":
            print(f"Executing BUY order for {quantity} of {symbol}")
            self.buy(symbol, quantity)
        elif signal.upper() == "SELL":
            print(f"Executing SELL order for {quantity} of {symbol}")
            self.sell(symbol, quantity)
        else:
            print(f"Unknown signal: {signal} for {symbol}")

    def get_account_summary(self):
        """
        Get account summary information.
        
        Returns:
            dict: Account summary information
        """
        print("Fetching account summary")
        # TODO: Implement real account summary fetching
        return {"NetLiquidation": 100000.0}  # Placeholder 