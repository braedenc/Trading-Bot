#!/usr/bin/env python3
"""
Test script to demonstrate strategy selection functionality
"""

import sys
import asyncio
import pytest
sys.path.append('.')

from trading_bot.test_sma_simple import generate_mock_price_data
from datetime import datetime

def discover_strategies():
    """Discover available trading strategies."""
    strategies = {}
    
    try:
        from trading_bot.agents.sma_agent import SMAAgent
        strategies['sma'] = {
            'name': 'SMA Crossover',
            'agent_class': SMAAgent,
            'description': 'Simple Moving Average crossover strategy',
            'params': {'fast_period': 10, 'slow_period': 20}
        }
    except ImportError:
        pass
    
    try:
        from trading_bot.agents.github_agent import GitHubAgent
        strategies['github'] = {
            'name': 'GitHub AI Strategy',
            'agent_class': GitHubAgent,
            'description': 'AI hedge fund strategy from external repo',
            'params': {'strategy_name': 'ai_hedge_fund'}
        }
    except ImportError:
        pass
    
    return strategies

@pytest.mark.asyncio
async def test_strategy_comparison():
    """Test multiple strategies side by side."""
    print("⚖️  STRATEGY COMPARISON TEST")
    print("=" * 50)
    
    strategies = discover_strategies()
    print(f"Found {len(strategies)} strategies to test\n")
    
    # Generate consistent test data
    test_data = generate_mock_price_data("COMPARISON", 200)
    
    results = {}
    
    for strategy_key, strategy_info in strategies.items():
        try:
            print(f"🎯 Testing {strategy_info['name']}:")
            
            # Create agent
            agent_class = strategy_info['agent_class']
            if 'params' in strategy_info:
                agent = agent_class(**strategy_info['params'])
            else:
                agent = agent_class()
            
            total_signals = 0
            buy_signals = 0
            sell_signals = 0
            
            # Test signals over time windows
            for i in range(50, len(test_data['historical']), 10):
                snapshot = {
                    'prices': {'COMPARISON': {
                        'historical': test_data['historical'][:i+1],
                        'current_price': test_data['historical'][i]['close']
                    }},
                    'positions': {'COMPARISON': 0},
                    'timestamp': test_data['historical'][i]['timestamp']
                }
                
                signals = await agent.generate_signals(snapshot)
                total_signals += len(signals)
                
                for signal in signals:
                    if signal['action'] == 'buy':
                        buy_signals += 1
                    elif signal['action'] == 'sell':
                        sell_signals += 1
            
            results[strategy_key] = {
                'name': strategy_info['name'],
                'total_signals': total_signals,
                'buy_signals': buy_signals,
                'sell_signals': sell_signals,
                'signal_frequency': total_signals / ((len(test_data['historical'])-50)/10) * 100
            }
            
            print(f"   Total signals: {total_signals}")
            print(f"   Buy signals: {buy_signals}")
            print(f"   Sell signals: {sell_signals}")
            print(f"   Signal frequency: {total_signals / ((len(test_data['historical'])-50)/10) * 100:.1f}%")
            print()
            
        except Exception as e:
            print(f"❌ Error testing {strategy_info['name']}: {e}")
    
    print("🏆 COMPARISON SUMMARY:")
    print("-" * 40)
    sorted_strategies = sorted(results.items(), key=lambda x: x[1]['total_signals'], reverse=True)
    
    for i, (key, result) in enumerate(sorted_strategies, 1):
        print(f"{i}. {result['name']:20} - {result['total_signals']} signals ({result['signal_frequency']:.1f}% frequency)")
    
    print("\n✅ Strategy comparison complete!")

@pytest.mark.asyncio
async def test_paper_trading_with_strategy():
    """Test paper trading with strategy selection."""
    print("📊 PAPER TRADING WITH MULTIPLE STRATEGIES")
    print("=" * 50)
    
    strategies = discover_strategies()
    
    # Generate market data
    mock_data = generate_mock_price_data("MULTI", 100)
    
    for strategy_key, strategy_info in strategies.items():
        try:
            print(f"\n🤖 Testing {strategy_info['name']}...")
            
            # Create agent
            agent_class = strategy_info['agent_class']
            if 'params' in strategy_info:
                agent = agent_class(**strategy_info['params'])
            else:
                agent = agent_class()
            
            snapshot = {
                'prices': {'MULTI': mock_data},
                'positions': {'MULTI': 0},
                'timestamp': datetime.now()
            }
            
            signals = await agent.generate_signals(snapshot)
            
            print(f"📢 {strategy_info['name']} generated {len(signals)} signals:")
            for signal in signals:
                print(f"   {signal['action'].upper()}: {signal['quantity']:.2f} {signal['symbol']}")
                print(f"   Confidence: {signal['confidence']:.1%}")
            
            if not signals:
                print("   No signals generated")
                
        except Exception as e:
            print(f"❌ Error testing {strategy_info['name']}: {e}")
    
    print("\n✅ Multi-strategy paper trading complete!")

def main():
    """Main test function."""
    print("🤖 STRATEGY SELECTION DEMONSTRATION")
    print("=" * 60)
    
    strategies = discover_strategies()
    print("📊 DISCOVERED STRATEGIES:")
    print("-" * 30)
    for key, strategy in strategies.items():
        print(f"✅ {strategy['name']:20} - {strategy['description']}")
    
    if not strategies:
        print("❌ No strategies found")
        return
    
    print(f"\nRunning tests with {len(strategies)} strategies...")
    
    # Run tests
    asyncio.run(test_paper_trading_with_strategy())
    print("\n" + "="*60 + "\n")
    asyncio.run(test_strategy_comparison())

if __name__ == "__main__":
    main()