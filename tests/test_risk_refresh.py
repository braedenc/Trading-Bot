import pytest, asyncio
from trading_bot.engine.risk import RiskManager

class DummySB:
    async def fetch_risk_limits(self):
        return [
            {'scope': 'global', 'max_notional': 100000},
            {'scope': 'github_agent', 'max_notional': 25000},
        ]

@pytest.mark.asyncio
async def test_refresh_limits():
    r = RiskManager({}, {})
    await r.refresh_limits(DummySB())
    assert r.global_limits['max_notional'] == 100000
    assert r.per_agent_limits['github_agent']['max_notional'] == 25000 