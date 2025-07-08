#!/usr/bin/env python3
"""
Manual Cursor Agent Runner
Use this while troubleshooting Cursor UI access to agents
"""

import sys
import subprocess
import os

AGENTS = {
    "smoke-test": "Run unit tests + SMA agent sanity check",
    "paper-trade-sim": "Simulate paper trading session with SMA agent", 
    "performance-benchmark": "Run comprehensive performance benchmarks",
    "agent-health-check": "Verify all trading agents load correctly",
    "quick-backtest": "Run a quick backtest on historical data",
    "strategy-analyze": "Analyze and compare different SMA strategy parameters",
    "dev-setup": "Setup development environment and verify dependencies",
    "clean-repo": "Clean up temporary files and reset workspace",
    "docs-update": "Update documentation and generate performance reports"
}

def show_menu():
    print("🤖 CURSOR AGENTS - MANUAL RUNNER")
    print("=" * 50)
    print("Available agents:")
    for i, (agent, desc) in enumerate(AGENTS.items(), 1):
        print(f"  {i}. {agent:20} - {desc}")
    print("  0. Exit")
    print("=" * 50)

def run_smoke_test():
    print("🧪 Running smoke-test agent...")
    subprocess.run(["python3", "trading_bot/test_sma_simple.py"])

def run_paper_trade_sim():
    print("📊 Running paper-trade-sim agent...")
    script = '''
import asyncio
import sys
import os
sys.path.append('.')

from trading_bot.agents.sma_agent import SMAAgent
from trading_bot.test_sma_simple import generate_mock_price_data
from datetime import datetime

async def run_paper_simulation():
    print("🤖 Initializing SMA Agent...")
    agent = SMAAgent(fast_period=10, slow_period=20)
    
    print("📈 Generating market data...")
    mock_data = generate_mock_price_data("AAPL", 100)
    
    snapshot = {
        'prices': {'AAPL': mock_data},
        'positions': {'AAPL': 0},
        'timestamp': datetime.now()
    }
    
    print("🔍 Generating signals...")
    signals = await agent.generate_signals(snapshot)
    
    print(f"📢 Generated {len(signals)} signals:")
    for signal in signals:
        print(f"   {signal['action'].upper()}: {signal['quantity']:.2f} {signal['symbol']}")
        print(f"   Reason: {signal['reasoning']}")
        print(f"   Confidence: {signal['confidence']:.1%}")
    
    if not signals:
        print("   No signals generated (insufficient crossover conditions)")
    
    print("✅ Paper trading simulation complete")

asyncio.run(run_paper_simulation())
'''
    subprocess.run(["python3", "-c", script])

def run_agent_health_check():
    print("🏥 Running agent-health-check agent...")
    script = '''
import sys
import os
sys.path.append('.')

def check_agent_health():
    print("🔍 Checking agent imports...")
    
    try:
        from trading_bot.base_agent import BaseAgent
        print("✅ BaseAgent imported successfully")
    except Exception as e:
        print(f"❌ BaseAgent import failed: {e}")
        return False
    
    try:
        from trading_bot.agents.sma_agent import SMAAgent
        print("✅ SMAAgent imported successfully")
        
        # Test instantiation
        agent = SMAAgent()
        print(f"✅ SMAAgent created: {agent.name}")
        print(f"   Fast period: {agent.fast_period}")
        print(f"   Slow period: {agent.slow_period}")
        
    except Exception as e:
        print(f"❌ SMAAgent import/creation failed: {e}")
        return False
    
    print("\\n📊 Agent health check complete!")
    return True

check_agent_health()
'''
    subprocess.run(["python3", "-c", script])

def run_performance_benchmark():
    print("🏃‍♂️ Running performance-benchmark agent...")
    script = '''
import time
import sys
import os
sys.path.append('.')

from trading_bot.test_sma_simple import generate_mock_price_data, simple_sma

def benchmark_sma_performance():
    print("=" * 60)
    print("📊 SMA PERFORMANCE BENCHMARK")
    print("=" * 60)
    
    test_sizes = [1000, 5000, 10000]
    
    for size in test_sizes:
        print(f"\\n🔧 Testing with {size:,} data points:")
        
        # Generate data
        start = time.time()
        data = generate_mock_price_data("TEST", size)
        data_time = time.time() - start
        
        prices = [p['close'] for p in data['historical']]
        
        # Calculate SMAs
        start = time.time()
        sma_calculations = 0
        
        for i in range(20, len(prices)):
            sma_10 = simple_sma(prices[:i+1], 10)
            sma_20 = simple_sma(prices[:i+1], 20)
            sma_calculations += 2
        
        calc_time = time.time() - start
        
        print(f"   Data generation: {data_time:.3f}s")
        print(f"   SMA calculations: {calc_time:.3f}s ({sma_calculations:,} ops)")
        print(f"   Avg per calculation: {calc_time/sma_calculations*1000:.3f}ms")
        print(f"   Throughput: {sma_calculations/calc_time:,.0f} calc/sec")
    
    print(f"\\n✅ Benchmark complete!")

benchmark_sma_performance()
'''
    subprocess.run(["python3", "-c", script])

def run_dev_setup():
    print("🔧 Running dev-setup agent...")
    script = '''
import sys
import subprocess
import os

def check_dev_setup():
    print("🔧 Setting up development environment...")
    
    # Check Python version
    print("🐍 Python version:")
    subprocess.run(["python3", "--version"])
    
    print("\\n📦 Checking core dependencies...")
    
    required = ['asyncio', 'datetime', 'logging', 'subprocess', 'os', 'sys']
    optional = ['numpy', 'pandas', 'matplotlib', 'plotly', 'jupyter']
    
    print("Core dependencies:")
    for module in required:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module} - MISSING")
    
    print("\\nOptional dependencies:")
    for module in optional:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ⚠️  {module} - not installed")
    
    print("\\n📁 Project structure verification:")
    if os.path.exists("trading_bot/"):
        print("  ✅ trading_bot/ directory exists")
        if os.path.exists("trading_bot/agents/"):
            print("  ✅ trading_bot/agents/ directory exists")
            agent_files = os.listdir("trading_bot/agents/")
            print(f"  📋 Available agent files: {len(agent_files)}")
            for f in agent_files:
                if f.endswith('.py'):
                    print(f"    - {f}")
        else:
            print("  ❌ trading_bot/agents/ directory missing")
    else:
        print("  ❌ trading_bot/ directory missing")
    
    print("\\n✅ Development environment check complete!")

check_dev_setup()
'''
    subprocess.run(["python3", "-c", script])

def run_clean_repo():
    print("🧹 Running clean-repo agent...")
    script = '''
import os
import subprocess
import glob

def clean_repository():
    print("🧹 Cleaning up workspace...")
    
    # Remove Python cache files
    print("🗑️  Removing Python cache files...")
    
    # Find and remove __pycache__ directories
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            try:
                import shutil
                shutil.rmtree(pycache_path)
                print(f"  Removed: {pycache_path}")
            except Exception as e:
                print(f"  Could not remove {pycache_path}: {e}")
    
    # Remove .pyc files
    pyc_files = glob.glob('**/*.pyc', recursive=True)
    for f in pyc_files:
        try:
            os.remove(f)
            print(f"  Removed: {f}")
        except Exception as e:
            print(f"  Could not remove {f}: {e}")
    
    # Remove .pyo files  
    pyo_files = glob.glob('**/*.pyo', recursive=True)
    for f in pyo_files:
        try:
            os.remove(f)
            print(f"  Removed: {f}")
        except Exception as e:
            print(f"  Could not remove {f}: {e}")
    
    # Remove log files
    print("🗑️  Removing temporary test files...")
    log_files = glob.glob('*.log') + glob.glob('trading_bot/*.log')
    for f in log_files:
        try:
            os.remove(f)
            print(f"  Removed: {f}")
        except Exception as e:
            print(f"  Could not remove {f}: {e}")
    
    # Show git status if available
    print("📊 Workspace status:")
    try:
        subprocess.run(["git", "status", "--porcelain"], check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("  Not a git repository or git not available")
    
    print("✅ Cleanup complete!")

clean_repository()
'''
    subprocess.run(["python3", "-c", script])

def run_quick_backtest():
    print("⏪ Running quick-backtest agent...")
    script = '''
import asyncio
import sys
import os
sys.path.append('.')

from trading_bot.agents.sma_agent import SMAAgent
from trading_bot.test_sma_simple import generate_mock_price_data
from datetime import datetime, timedelta

async def run_backtest():
    print("📈 SMA STRATEGY BACKTEST")
    print("=" * 40)
    
    # Generate longer historical data
    agent = SMAAgent(fast_period=5, slow_period=15)
    data = generate_mock_price_data("TEST", 250)  # ~1 year of data
    
    positions = {'TEST': 0}
    portfolio_value = 10000  # Start with $10k
    trades = []
    
    print(f"🏦 Starting portfolio value: ${portfolio_value:,.2f}")
    print(f"📊 Processing {len(data['historical'])} data points...")
    
    # Simulate trading over time
    for i in range(50, len(data['historical'])):
        # Create snapshot with data up to point i
        historical_slice = data['historical'][:i+1]
        snapshot = {
            'prices': {'TEST': {'historical': historical_slice, 'current_price': historical_slice[-1]['close']}},
            'positions': positions.copy(),
            'timestamp': historical_slice[-1]['timestamp']
        }
        
        signals = await agent.generate_signals(snapshot)
        
        for signal in signals:
            if signal['action'] == 'buy' and positions['TEST'] <= 0:
                price = historical_slice[-1]['close']
                shares = portfolio_value * 0.95 / price  # Use 95% of portfolio
                positions['TEST'] = shares
                portfolio_value = portfolio_value * 0.05  # Keep 5% cash
                trades.append(('BUY', shares, price, historical_slice[-1]['timestamp']))
                
            elif signal['action'] == 'sell' and positions['TEST'] > 0:
                price = historical_slice[-1]['close']
                portfolio_value += positions['TEST'] * price
                trades.append(('SELL', positions['TEST'], price, historical_slice[-1]['timestamp']))
                positions['TEST'] = 0
    
    # Final portfolio value
    final_price = data['historical'][-1]['close']
    if positions['TEST'] > 0:
        portfolio_value += positions['TEST'] * final_price
    
    print(f"\\n📊 BACKTEST RESULTS:")
    print(f"   Total trades: {len(trades)}")
    print(f"   Final portfolio value: ${portfolio_value:,.2f}")
    print(f"   Total return: {((portfolio_value/10000-1)*100):+.1f}%")
    
    if trades:
        print(f"\\n📋 Recent trades:")
        for trade in trades[-3:]:
            action, shares, price, timestamp = trade
            print(f"   {action}: {shares:.2f} shares @ ${price:.2f}")
    
    print("✅ Backtest complete!")

asyncio.run(run_backtest())
'''
    subprocess.run(["python3", "-c", script])

def run_strategy_analyze():
    print("📊 Running strategy-analyze agent...")
    script = '''
import asyncio
import sys
import os
sys.path.append('.')

from trading_bot.agents.sma_agent import SMAAgent
from trading_bot.test_sma_simple import generate_mock_price_data

async def analyze_strategies():
    print("🔍 STRATEGY PARAMETER ANALYSIS")
    print("=" * 50)
    
    # Different parameter combinations to test
    strategies = [
        (5, 10, "Very Fast"),
        (10, 20, "Fast"),
        (20, 50, "Medium"),
        (50, 100, "Slow")
    ]
    
    # Generate consistent test data
    data = generate_mock_price_data("ANALYSIS", 200)
    
    print(f"📈 Testing {len(strategies)} strategy combinations on {len(data['historical'])} data points\\n")
    
    for fast, slow, name in strategies:
        print(f"🎯 {name} Strategy (SMA {fast}/{slow}):")
        
        agent = SMAAgent(fast_period=fast, slow_period=slow)
        
        signal_count = 0
        buy_signals = 0
        sell_signals = 0
        
        # Test signals over time windows
        for i in range(max(fast, slow) + 10, len(data['historical']), 5):
            snapshot = {
                'prices': {'ANALYSIS': {
                    'historical': data['historical'][:i+1],
                    'current_price': data['historical'][i]['close']
                }},
                'positions': {'ANALYSIS': 0},
                'timestamp': data['historical'][i]['timestamp']
            }
            
            signals = await agent.generate_signals(snapshot)
            signal_count += len(signals)
            
            for signal in signals:
                if signal['action'] == 'buy':
                    buy_signals += 1
                elif signal['action'] == 'sell':
                    sell_signals += 1
        
        print(f"   Total signals: {signal_count}")
        print(f"   Buy signals: {buy_signals}")
        print(f"   Sell signals: {sell_signals}")
        print(f"   Signal frequency: {signal_count/((len(data['historical'])-max(fast,slow)-10)/5)*100:.1f}%")
        print()
    
    print("✅ Strategy analysis complete!")

asyncio.run(analyze_strategies())
'''
    subprocess.run(["python3", "-c", script])

def run_docs_update():
    print("📚 Running docs-update agent...")
    script = '''
import datetime
import os

def update_documentation():
    print("📚 Updating project documentation...")
    
    # Generate current timestamp
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Create/update performance summary
    report_content = f"""# Trading Bot Agent Performance Report

Generated: {timestamp}

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
"""
    
    try:
        with open('AGENT_PERFORMANCE_REPORT.md', 'w') as f:
            f.write(report_content)
        print("📄 Generated AGENT_PERFORMANCE_REPORT.md")
    except Exception as e:
        print(f"❌ Could not write report: {e}")
    
    print("✅ Documentation update complete!")

update_documentation()
'''
    subprocess.run(["python3", "-c", script])

def main():
    if len(sys.argv) > 1:
        agent_name = sys.argv[1]
        if agent_name in AGENTS:
            run_agent_by_name(agent_name)
            return
        else:
            print(f"❌ Unknown agent: {agent_name}")
            print(f"Available agents: {', '.join(AGENTS.keys())}")
            return
    
    while True:
        show_menu()
        choice = input("\\nSelect agent (1-9) or 0 to exit: ").strip()
        
        if choice == "0":
            print("👋 Goodbye!")
            break
        elif choice == "1":
            run_smoke_test()
        elif choice == "2":
            run_paper_trade_sim()
        elif choice == "3":
            run_performance_benchmark()
        elif choice == "4":
            run_agent_health_check()
        elif choice == "5":
            run_quick_backtest()
        elif choice == "6":
            run_strategy_analyze()
        elif choice == "7":
            run_dev_setup()
        elif choice == "8":
            run_clean_repo()
        elif choice == "9":
            run_docs_update()
        else:
            print("❌ Invalid choice. Please try again.")
        
        input("\\nPress Enter to continue...")

def run_agent_by_name(agent_name):
    """Run agent by name from command line"""
    agents_map = {
        "smoke-test": run_smoke_test,
        "paper-trade-sim": run_paper_trade_sim,
        "performance-benchmark": run_performance_benchmark,
        "agent-health-check": run_agent_health_check,
        "dev-setup": run_dev_setup,
        "clean-repo": run_clean_repo,
        "quick-backtest": run_quick_backtest,
        "strategy-analyze": run_strategy_analyze,
        "docs-update": run_docs_update,
    }
    
    if agent_name in agents_map:
        agents_map[agent_name]()
    else:
        print(f"🚧 Agent '{agent_name}' not implemented in manual runner yet")

if __name__ == "__main__":
    main()