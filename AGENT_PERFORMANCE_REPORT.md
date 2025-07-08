# Trading Bot Agent Performance Report

Generated: 2025-07-08 18:15:01

## Agent Status

### SMA Agent
- Status: ✅ Active
- Strategy: Simple Moving Average Crossover
- Performance: Optimized for high-frequency calculations
- Test Coverage: Full unit tests available

### Available Test Commands
```bash
# Quick smoke test
python3 trading_bot/test_sma_simple.py

# Full test suite  
python3 trading_bot/test_sma_agent.py

# Performance debugging
python3 trading_bot/debug_sma_performance.py
```

## Cursor Agents Available

| Agent | Purpose | Use Case |
|-------|---------|----------|
| `smoke-test` | Quick validation | Before every commit |
| `paper-trade-sim` | Strategy simulation | Development testing |
| `performance-benchmark` | Speed testing | Performance tuning |
| `agent-health-check` | System validation | Debug import issues |
| `quick-backtest` | Strategy validation | Historical testing |
| `strategy-analyze` | Parameter tuning | Strategy optimization |

## Next Steps
- Add live market data integration
- Implement risk management layer
- Add more technical indicators
- Create dashboard UI

## Access Methods
1. **Cursor UI**: Cmd+Shift+P → "Tasks: Run Task" → Select agent
2. **Command Line**: python3 run_agent.py [agent-name]
3. **Interactive Menu**: python3 run_agent.py

Generated automatically by docs-update agent.
