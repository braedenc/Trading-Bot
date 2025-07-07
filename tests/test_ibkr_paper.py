import pytest, asyncio
from trading_bot.engine.broker.ibkr_paper import IBKRBroker

class DummyIB(IBKRBroker):
    def __init__(self): pass   # skip actual connect
    async def execute_orders(self, orders): self.last = orders

@pytest.mark.asyncio
async def test_execute_orders():
    broker = DummyIB()
    orders = [{"symbol":"AAPL", "side":"BUY", "qty":1}]
    await broker.execute_orders(orders)
    assert broker.last[0]["symbol"] == "AAPL" 