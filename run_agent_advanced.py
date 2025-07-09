#!/usr/bin/env python3
"""
Advanced Cursor Agent Runner with Strategy Selection
Supports multiple trading strategies and interactive selection
"""

import sys
import subprocess
import os
import importlib.util

def discover_available_strategies():
    """Dynamically discover available trading strategies."""
    strategies = {}
    
    # Check for SMA Agent
    try:
        sys.path.append('.')
        from trading_bot.agents.sma_agent import SMAAgent
        strategies['sma'] = {
            'name': 'SMA Crossover',
            'module': 'trading_bot.agents.sma_agent',
            'class_name': 'SMAAgent',
            'description': 'Simple Moving Average crossover strategy',
            'params': {'fast_period': 10, 'slow_period': 20}
        }
    except ImportError:
        pass
    
    # Check for other agents
    try:
        from trading_bot.agents.github_agent import GitHubAgent
        strategies['github'] = {
            'name': 'GitHub AI Strategy',
            'module': 'trading_bot.agents.github_agent',
            'class_name': 'GitHubAgent',
            'description': 'AI hedge fund strategy from external repo',
            'params': {'strategy_name': 'ai_hedge_fund'}
        }
    except ImportError:
        pass
    
    try:
        from trading_bot.agents.optimized_technicals import OptimizedTechnicalAgent
        strategies['technical'] = {
            'name': 'Optimized Technical',
            'module': 'trading_bot.agents.optimized_technicals',
            'class_name': 'OptimizedTechnicalAgent',
            'description': 'Multi-indicator technical analysis',
            'params': {}
        }
    except ImportError:
        pass
    
    return strategies

def show_strategy_menu():
    """Display available strategies for selection."""
    strategies = discover_available_strategies()
    
    print("📊 AVAILABLE TRADING STRATEGIES")
    print("=" * 50)
    if not strategies:
        print("❌ No trading strategies found!")
        return {}, []
        
    strategy_list = list(strategies.items())
    for i, (key, strategy) in enumerate(strategy_list, 1):
        print(f"  {i}. {strategy['name']:20} - {strategy['description']}")
    
    print("  0. All strategies (comparison mode)")
    print("=" * 50)
    
    return strategies, strategy_list

def get_strategy_choice(strategies, strategy_list):
    """Get user's strategy selection."""
    while True:
        try:
            choice = input("Select strategy (1-{}, 0 for all): ".format(len(strategy_list))).strip()
            
            if choice == "0":
                return "all", strategies
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(strategy_list):
                key, strategy = strategy_list[choice_num - 1]
                return key, strategy
            else:
                print("❌ Invalid choice. Please try again.")
        except (ValueError, KeyboardInterrupt):
            print("❌ Invalid input. Please enter a number.")

def run_paper_trade_with_strategy():
    """Paper trading with strategy selection."""
    print("📊 PAPER TRADING WITH STRATEGY SELECTION")
    print("=" * 50)
    
    strategies, strategy_list = show_strategy_menu()
    if not strategies:
        print("❌ No strategies available for testing")
        return
    
    strategy_key, strategy_info = get_strategy_choice(strategies, strategy_list)
    
    if strategy_key == "all":
        print("🔄 Running paper trading with ALL strategies...")
        script = f'''
import asyncio
import sys
import os
sys.path.append('.')

from trading_bot.test_sma_simple import generate_mock_price_data
from datetime import datetime

async def run_multi_strategy_simulation():
    strategies_to_test = {repr(strategies)}
    
    print("📈 Generating market data...")
    mock_data = generate_mock_price_data("MULTI", 100)
    
    results = {{}}
    
             for strategy_key, strategy_info in strategies_to_test.items():
             try:
                 print(f"\\n🤖 Testing {{strategy_info['name']}}...")
                 
                 # Import and create agent dynamically
                 module_name = strategy_info['module']
                 class_name = strategy_info['class_name']
                 module = __import__(module_name, fromlist=[class_name])
                 agent_class = getattr(module, class_name)
                 
                 if 'params' in strategy_info:
                     agent = agent_class(**strategy_info['params'])
                 else:
                     agent = agent_class()
            
            snapshot = {{
                'prices': {{'MULTI': mock_data}},
                'positions': {{'MULTI': 0}},
                'timestamp': datetime.now()
            }}
            
            signals = await agent.generate_signals(snapshot)
            results[strategy_key] = signals
            
            print(f"📢 {{strategy_info['name']}} generated {{len(signals)}} signals:")
            for signal in signals:
                print(f"   {{signal['action'].upper()}}: {{signal['quantity']:.2f}} {{signal['symbol']}}")
                print(f"   Confidence: {{signal['confidence']:.1%}}")
            
            if not signals:
                print("   No signals generated")
                
        except Exception as e:
            print(f"❌ Error testing {{strategy_info['name']}}: {{e}}")
    
    print("\\n✅ Multi-strategy paper trading complete!")

asyncio.run(run_multi_strategy_simulation())
'''
    else:
        print(f"🤖 Running paper trading with {strategy_info['name']}...")
        script = f'''
import asyncio
import sys
import os
sys.path.append('.')

from trading_bot.test_sma_simple import generate_mock_price_data
from datetime import datetime

async def run_single_strategy_simulation():
    strategy_info = {repr(strategy_info)}
    
         print(f"🤖 Initializing {{strategy_info['name']}}...")
     
     # Import and create agent dynamically
     module_name = strategy_info['module']
     class_name = strategy_info['class_name']
     module = __import__(module_name, fromlist=[class_name])
     agent_class = getattr(module, class_name)
     
     if 'params' in strategy_info:
         agent = agent_class(**strategy_info['params'])
     else:
         agent = agent_class()
    
    print("📈 Generating market data...")
    mock_data = generate_mock_price_data("TEST", 100)
    
    snapshot = {{
        'prices': {{'TEST': mock_data}},
        'positions': {{'TEST': 0}},
        'timestamp': datetime.now()
    }}
    
    print("🔍 Generating signals...")
    signals = await agent.generate_signals(snapshot)
    
    print(f"📢 {{strategy_info['name']}} generated {{len(signals)}} signals:")
    for signal in signals:
        print(f"   {{signal['action'].upper()}}: {{signal['quantity']:.2f}} {{signal['symbol']}}")
        print(f"   Reason: {{signal['reasoning']}}")
        print(f"   Confidence: {{signal['confidence']:.1%}}")
    
    if not signals:
        print("   No signals generated (insufficient conditions)")
    
    print("✅ Paper trading simulation complete")

asyncio.run(run_single_strategy_simulation())
'''
    
    subprocess.run(["python3", "-c", script])

def run_strategy_comparison():
    """Compare multiple strategies side by side."""
    print("⚖️  STRATEGY COMPARISON ANALYSIS")
    print("=" * 50)
    
    strategies = discover_available_strategies()
    if len(strategies) < 2:
        print("❌ Need at least 2 strategies for comparison")
        return
    
    print("🔄 Running comparison on all available strategies...")
    
    script = f'''
import asyncio
import sys
import os
sys.path.append('.')

from trading_bot.test_sma_simple import generate_mock_price_data
from datetime import datetime

async def run_strategy_comparison():
    strategies_to_test = {repr(strategies)}
    
    print("📈 Generating consistent test data (500 data points)...")
    test_data = generate_mock_price_data("COMPARISON", 500)
    
    print("\\n🔍 STRATEGY COMPARISON RESULTS")
    print("=" * 60)
    
    results = {{}}
    
    for strategy_key, strategy_info in strategies_to_test.items():
        try:
            print(f"\\n🎯 Testing {{strategy_info['name']}}:")
            
            # Import and create agent
            agent_class = strategy_info['class']
            if 'params' in strategy_info:
                agent = agent_class(**strategy_info['params'])
            else:
                agent = agent_class()
            
            total_signals = 0
            buy_signals = 0
            sell_signals = 0
            
            # Test signals over time windows
            for i in range(50, len(test_data['historical']), 10):
                snapshot = {{
                    'prices': {{'COMPARISON': {{
                        'historical': test_data['historical'][:i+1],
                        'current_price': test_data['historical'][i]['close']
                    }}}},
                    'positions': {{'COMPARISON': 0}},
                    'timestamp': test_data['historical'][i]['timestamp']
                }}
                
                signals = await agent.generate_signals(snapshot)
                total_signals += len(signals)
                
                for signal in signals:
                    if signal['action'] == 'buy':
                        buy_signals += 1
                    elif signal['action'] == 'sell':
                        sell_signals += 1
            
            results[strategy_key] = {{
                'name': strategy_info['name'],
                'total_signals': total_signals,
                'buy_signals': buy_signals,
                'sell_signals': sell_signals,
                'signal_frequency': total_signals / ((len(test_data['historical'])-50)/10) * 100
            }}
            
            print(f"   Total signals: {{total_signals}}")
            print(f"   Buy signals: {{buy_signals}}")
            print(f"   Sell signals: {{sell_signals}}")
            print(f"   Signal frequency: {{total_signals / ((len(test_data['historical'])-50)/10) * 100:.1f}}%")
            
        except Exception as e:
            print(f"❌ Error testing {{strategy_info['name']}}: {{e}}")
    
    print("\\n🏆 COMPARISON SUMMARY:")
    print("-" * 40)
    sorted_strategies = sorted(results.items(), key=lambda x: x[1]['total_signals'], reverse=True)
    
    for i, (key, result) in enumerate(sorted_strategies, 1):
        print(f"{{i}}. {{result['name']:20}} - {{result['total_signals']}} signals ({{result['signal_frequency']:.1f}}% frequency)")
    
    print("\\n✅ Strategy comparison complete!")

asyncio.run(run_strategy_comparison())
'''
    
    subprocess.run(["python3", "-c", script])

def run_backtest_with_strategy():
    """Backtest with strategy selection."""
    print("⏪ BACKTESTING WITH STRATEGY SELECTION")
    print("=" * 50)
    
    strategies, strategy_list = show_strategy_menu()
    if not strategies:
        print("❌ No strategies available for backtesting")
        return
    
    strategy_key, strategy_info = get_strategy_choice(strategies, strategy_list)
    
    if strategy_key == "all":
        print("🔄 Running backtest on ALL strategies...")
        # Multi-strategy backtest code here
        print("🚧 Multi-strategy backtest coming soon!")
        return
    
    print(f"⏪ Running backtest with {strategy_info['name']}...")
    
    script = f'''
import asyncio
import sys
import os
sys.path.append('.')

from trading_bot.test_sma_simple import generate_mock_price_data
from datetime import datetime, timedelta

async def run_strategy_backtest():
    strategy_info = {repr(strategy_info)}
    
    print(f"📈 {{strategy_info['name'].upper()}} STRATEGY BACKTEST")
    print("=" * 50)
    
    # Import and create agent
    agent_class = strategy_info['class']
    if 'params' in strategy_info:
        agent = agent_class(**strategy_info['params'])
    else:
        agent = agent_class()
    
    data = generate_mock_price_data("BACKTEST", 250)  # ~1 year of data
    
    positions = {{'BACKTEST': 0}}
    portfolio_value = 10000  # Start with $10k
    trades = []
    
    print(f"🏦 Starting portfolio value: ${{portfolio_value:,.2f}}")
    print(f"📊 Processing {{len(data['historical'])}} data points...")
    print(f"🤖 Using strategy: {{strategy_info['name']}}")
    
    # Simulate trading over time
    for i in range(50, len(data['historical'])):
        historical_slice = data['historical'][:i+1]
        snapshot = {{
            'prices': {{'BACKTEST': {{'historical': historical_slice, 'current_price': historical_slice[-1]['close']}}}},
            'positions': positions.copy(),
            'timestamp': historical_slice[-1]['timestamp']
        }}
        
        signals = await agent.generate_signals(snapshot)
        
        for signal in signals:
            if signal['action'] == 'buy' and positions['BACKTEST'] <= 0:
                price = historical_slice[-1]['close']
                shares = portfolio_value * 0.95 / price
                positions['BACKTEST'] = shares
                portfolio_value = portfolio_value * 0.05
                trades.append(('BUY', shares, price, historical_slice[-1]['timestamp']))
                
            elif signal['action'] == 'sell' and positions['BACKTEST'] > 0:
                price = historical_slice[-1]['close']
                portfolio_value += positions['BACKTEST'] * price
                trades.append(('SELL', positions['BACKTEST'], price, historical_slice[-1]['timestamp']))
                positions['BACKTEST'] = 0
    
    # Final portfolio value
    final_price = data['historical'][-1]['close']
    if positions['BACKTEST'] > 0:
        portfolio_value += positions['BACKTEST'] * final_price
    
    print(f"\\n📊 BACKTEST RESULTS:")
    print(f"   Strategy: {{strategy_info['name']}}")
    print(f"   Total trades: {{len(trades)}}")
    print(f"   Final portfolio value: ${{portfolio_value:,.2f}}")
    print(f"   Total return: {{((portfolio_value/10000-1)*100):+.1f}}%")
    
    if trades:
        print(f"\\n📋 Recent trades:")
        for trade in trades[-3:]:
            action, shares, price, timestamp = trade
            print(f"   {{action}}: {{shares:.2f}} shares @ ${{price:.2f}}")
    
    print("✅ Backtest complete!")

asyncio.run(run_strategy_backtest())
'''
    
    subprocess.run(["python3", "-c", script])

def main():
    """Main menu for advanced agent runner."""
    print("🤖 ADVANCED CURSOR AGENTS - STRATEGY SELECTION")
    print("=" * 60)
    print("Available workflow agents:")
    print("  1. Paper Trade with Strategy Selection")
    print("  2. Strategy Comparison Analysis") 
    print("  3. Backtest with Strategy Selection")
    print("  4. List Available Strategies")
    print("  0. Exit")
    print("=" * 60)
    
    while True:
        choice = input("\\nSelect option (1-4) or 0 to exit: ").strip()
        
        if choice == "0":
            print("👋 Goodbye!")
            break
        elif choice == "1":
            run_paper_trade_with_strategy()
        elif choice == "2":
            run_strategy_comparison()
        elif choice == "3":
            run_backtest_with_strategy()
        elif choice == "4":
            strategies = discover_available_strategies()
            print("\\n📊 DISCOVERED STRATEGIES:")
            print("-" * 30)
            for key, strategy in strategies.items():
                print(f"✅ {strategy['name']:20} - {strategy['description']}")
            if not strategies:
                print("❌ No strategies found")
        else:
            print("❌ Invalid choice. Please try again.")
        
        input("\\nPress Enter to continue...")

if __name__ == "__main__":
    main()