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
        elif choice in ["5", "6", "7", "8", "9"]:
            print(f"🚧 Agent {choice} not implemented in manual runner yet")
            print("   (Use Cursor UI when available)")
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
    }
    
    if agent_name in agents_map:
        agents_map[agent_name]()
    else:
        print(f"🚧 Agent '{agent_name}' not implemented in manual runner yet")

if __name__ == "__main__":
    main()