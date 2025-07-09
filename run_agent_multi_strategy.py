#!/usr/bin/env python3
"""
Multi-Strategy Cursor Agent Runner
All 9 workflow agents enhanced with strategy selection capabilities
"""

import sys
import subprocess
import os
import json

def discover_available_strategies():
    """Dynamically discover available trading strategies."""
    strategies = {}
    
    try:
        sys.path.append('.')
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
    
    try:
        from trading_bot.agents.optimized_technicals import OptimizedTechnicalAgent
        strategies['technical'] = {
            'name': 'Optimized Technical',
            'agent_class': OptimizedTechnicalAgent,
            'description': 'Multi-indicator technical analysis',
            'params': {}
        }
    except ImportError:
        pass
    
    return strategies

def show_strategy_selection_menu(title="Select Strategy"):
    """Show strategy selection menu with all/individual options."""
    strategies = discover_available_strategies()
    
    print(f"📊 {title.upper()}")
    print("=" * 50)
    
    if not strategies:
        print("❌ No trading strategies found!")
        return None, None
    
    strategy_list = list(strategies.items())
    print("Available strategies:")
    
    for i, (key, strategy) in enumerate(strategy_list, 1):
        print(f"  {i}. {strategy['name']:20} - {strategy['description']}")
    
    print("  0. All strategies (comprehensive mode)")
    print("=" * 50)
    
    return strategies, strategy_list

def get_strategy_choice_input(strategies, strategy_list):
    """Get user's strategy selection input."""
    while True:
        try:
            choice = input(f"Select strategy (1-{len(strategy_list)}, 0 for all): ").strip()
            
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
            return None, None

def run_smoke_test_multi_strategy():
    """Enhanced smoke test with multi-strategy support."""
    print("🧪 MULTI-STRATEGY SMOKE TEST")
    print("=" * 50)
    
    strategies, strategy_list = show_strategy_selection_menu("Strategy Smoke Test")
    if not strategies or not strategy_list:
        print("❌ No strategies available for testing")
        return
    
    strategy_key, strategy_info = get_strategy_choice_input(strategies, strategy_list)
    if not strategy_key:
        print("❌ No strategy selected")
        return
    
    if strategy_key == "all":
        print("🔄 Running smoke test on ALL strategies...")
        
        # Test simple SMA tests first
        print("\n📋 Running basic SMA tests...")
        subprocess.run(["python3", "trading_bot/test_sma_simple.py"])
        
        # Test each strategy
        script = f'''
import sys
import asyncio
sys.path.append('.')

from trading_bot.test_sma_simple import generate_mock_price_data
from datetime import datetime

async def test_all_strategies():
    strategies = {repr(strategies)}
    
    print("\\n🤖 TESTING ALL STRATEGIES:")
    print("=" * 40)
    
    results = {{}}
    
    for strategy_key, strategy_info in strategies.items():
        try:
            print(f"\\n🎯 Testing {{strategy_info['name']}}...")
            
            # Create agent
            agent_class = strategy_info['agent_class']
            if 'params' in strategy_info:
                agent = agent_class(**strategy_info['params'])
            else:
                agent = agent_class()
            
            # Basic functionality test
            mock_data = generate_mock_price_data("SMOKE_TEST", 50)
            snapshot = {{
                'prices': {{'SMOKE_TEST': mock_data}},
                'positions': {{'SMOKE_TEST': 0}},
                'timestamp': datetime.now()
            }}
            
            signals = await agent.generate_signals(snapshot)
            
            results[strategy_key] = {{
                'name': strategy_info['name'],
                'success': True,
                'signals': len(signals),
                'error': None
            }}
            
            print(f"   ✅ {{strategy_info['name']}} - Working ({{len(signals)}} signals)")
            
        except Exception as e:
            results[strategy_key] = {{
                'name': strategy_info['name'],
                'success': False,
                'signals': 0,
                'error': str(e)
            }}
            print(f"   ❌ {{strategy_info['name']}} - Error: {{e}}")
    
    print("\\n📊 SMOKE TEST SUMMARY:")
    print("-" * 30)
    working = sum(1 for r in results.values() if r['success'])
    total = len(results)
    
    print(f"✅ Working strategies: {{working}}/{{total}}")
    
    for strategy_key, result in results.items():
        status = "✅" if result['success'] else "❌"
        print(f"   {{status}} {{result['name']:20}} - {{result['signals']}} signals")
    
    if working == total:
        print("\\n🎉 ALL STRATEGIES PASSED SMOKE TEST!")
    else:
        print(f"\\n⚠️  {{total - working}} strategies need attention")

asyncio.run(test_all_strategies())
'''
        subprocess.run(["python3", "-c", script])
    else:
        print(f"🎯 Running smoke test for {strategy_info['name']}...")
        # Single strategy smoke test
        subprocess.run(["python3", "trading_bot/test_sma_simple.py"])
        
        script = f'''
import sys
import asyncio
sys.path.append('.')

from trading_bot.test_sma_simple import generate_mock_price_data
from datetime import datetime

async def test_single_strategy():
    strategy_info = {repr(strategy_info)}
    
    print(f"🎯 Testing {{strategy_info['name']}}...")
    
    try:
        # Create agent
        agent_class = strategy_info['agent_class']
        if 'params' in strategy_info:
            agent = agent_class(**strategy_info['params'])
        else:
            agent = agent_class()
        
        # Test functionality
        mock_data = generate_mock_price_data("SMOKE_TEST", 50)
        snapshot = {{
            'prices': {{'SMOKE_TEST': mock_data}},
            'positions': {{'SMOKE_TEST': 0}},
            'timestamp': datetime.now()
        }}
        
        signals = await agent.generate_signals(snapshot)
        
        print(f"✅ {{strategy_info['name']}} smoke test PASSED")
        print(f"   Generated {{len(signals)}} signals")
        print(f"   Agent initialized successfully")
        print(f"   Signal generation working")
        
    except Exception as e:
        print(f"❌ {{strategy_info['name']}} smoke test FAILED: {{e}}")

asyncio.run(test_single_strategy())
'''
        subprocess.run(["python3", "-c", script])

def run_performance_benchmark_multi_strategy():
    """Enhanced performance benchmark with multi-strategy support."""
    print("🏃‍♂️ MULTI-STRATEGY PERFORMANCE BENCHMARK")
    print("=" * 50)
    
    strategies, strategy_list = show_strategy_selection_menu("Strategy Performance Test")
    if not strategies:
        return
    
    strategy_key, strategy_info = get_strategy_choice_input(strategies, strategy_list)
    if not strategy_key:
        return
    
    if strategy_key == "all":
        print("🔄 Running performance benchmark on ALL strategies...")
        
        script = f'''
import time
import sys
import asyncio
sys.path.append('.')

from trading_bot.test_sma_simple import generate_mock_price_data

async def benchmark_all_strategies():
    strategies = {repr(strategies)}
    
    print("⚡ MULTI-STRATEGY PERFORMANCE BENCHMARK")
    print("=" * 60)
    
    test_sizes = [1000, 5000, 10000]
    
    for size in test_sizes:
        print(f"\\n🔧 Testing with {{size:,}} data points:")
        print("-" * 40)
        
        for strategy_key, strategy_info in strategies.items():
            try:
                # Create agent
                agent_class = strategy_info['agent_class']
                if 'params' in strategy_info:
                    agent = agent_class(**strategy_info['params'])
                else:
                    agent = agent_class()
                
                # Generate test data
                data = generate_mock_price_data("BENCHMARK", size)
                
                # Time the signal generation
                start_time = time.time()
                
                snapshot = {{
                    'prices': {{'BENCHMARK': data}},
                    'positions': {{'BENCHMARK': 0}},
                    'timestamp': data['timestamp']
                }}
                
                signals = await agent.generate_signals(snapshot)
                
                calc_time = time.time() - start_time
                
                print(f"   {{strategy_info['name']:20}} - {{calc_time:.3f}}s ({{len(signals)}} signals)")
                
            except Exception as e:
                print(f"   {{strategy_info['name']:20}} - ERROR: {{e}}")
        
        print()
    
    print("✅ Multi-strategy benchmark complete!")

asyncio.run(benchmark_all_strategies())
'''
        subprocess.run(["python3", "-c", script])
    else:
        print(f"🎯 Running performance benchmark for {strategy_info['name']}...")
        # Single strategy performance test (existing logic)
        script = f'''
import time
import sys
import asyncio
sys.path.append('.')

from trading_bot.test_sma_simple import generate_mock_price_data

async def benchmark_single_strategy():
    strategy_info = {repr(strategy_info)}
    
    print(f"⚡ {{strategy_info['name'].upper()}} PERFORMANCE BENCHMARK")
    print("=" * 60)
    
    test_sizes = [1000, 5000, 10000]
    
    for size in test_sizes:
        print(f"\\n🔧 Testing with {{size:,}} data points:")
        
        try:
            # Create agent
            agent_class = strategy_info['agent_class']
            if 'params' in strategy_info:
                agent = agent_class(**strategy_info['params'])
            else:
                agent = agent_class()
            
            # Generate test data
            start = time.time()
            data = generate_mock_price_data("BENCHMARK", size)
            data_time = time.time() - start
            
            # Time signal generation
            start = time.time()
            snapshot = {{
                'prices': {{'BENCHMARK': data}},
                'positions': {{'BENCHMARK': 0}},
                'timestamp': data['timestamp']
            }}
            
            signals = await agent.generate_signals(snapshot)
            calc_time = time.time() - start
            
            print(f"   Data generation: {{data_time:.3f}}s")
            print(f"   Signal generation: {{calc_time:.3f}}s")
            print(f"   Signals generated: {{len(signals)}}")
            print(f"   Processing rate: {{size/calc_time:,.0f}} points/sec")
            
        except Exception as e:
            print(f"   ERROR: {{e}}")
    
    print("\\n✅ Performance benchmark complete!")

asyncio.run(benchmark_single_strategy())
'''
        subprocess.run(["python3", "-c", script])

def run_agent_health_check_multi_strategy():
    """Enhanced agent health check with multi-strategy support."""
    print("🏥 MULTI-STRATEGY AGENT HEALTH CHECK")
    print("=" * 50)
    
    # Always check all strategies for health
    script = f'''
import sys
import os
sys.path.append('.')

def check_all_strategies_health():
    print("🔍 Checking all trading strategies...")
    
    strategies_tested = {{}}
    
    # Check base agent
    try:
        from trading_bot.base_agent import BaseAgent
        print("✅ BaseAgent imported successfully")
    except Exception as e:
        print(f"❌ BaseAgent import failed: {{e}}")
        return False
    
    # Check SMA Agent
    try:
        from trading_bot.agents.sma_agent import SMAAgent
        agent = SMAAgent()
        strategies_tested['SMA Crossover'] = {{
            'status': 'healthy',
            'details': f'Fast: {{agent.fast_period}}, Slow: {{agent.slow_period}}'
        }}
        print(f"✅ SMAAgent: {{agent.name}} ({{agent.fast_period}}/{{agent.slow_period}})")
    except Exception as e:
        strategies_tested['SMA Crossover'] = {{'status': 'error', 'details': str(e)}}
        print(f"❌ SMAAgent failed: {{e}}")
    
    # Check GitHub Agent
    try:
        from trading_bot.agents.github_agent import GitHubAgent
        agent = GitHubAgent("test")
        strategies_tested['GitHub AI Strategy'] = {{
            'status': 'healthy',
            'details': f'Strategy: {{agent.strategy_name}}'
        }}
        print(f"✅ GitHubAgent: {{agent.name}}")
    except Exception as e:
        strategies_tested['GitHub AI Strategy'] = {{'status': 'error', 'details': str(e)}}
        print(f"❌ GitHubAgent failed: {{e}}")
    
    # Check Optimized Technical Agent
    try:
        from trading_bot.agents.optimized_technicals import OptimizedTechnicalAgent
        agent = OptimizedTechnicalAgent()
        strategies_tested['Optimized Technical'] = {{
            'status': 'healthy',
            'details': 'Multi-indicator analysis'
        }}
        print(f"✅ OptimizedTechnicalAgent: {{agent.name}}")
    except Exception as e:
        strategies_tested['Optimized Technical'] = {{'status': 'error', 'details': str(e)}}
        print(f"⚠️  OptimizedTechnicalAgent failed: {{e}}")
    
    # Health summary
    print("\\n📊 STRATEGY HEALTH SUMMARY:")
    print("-" * 40)
    
    healthy_count = sum(1 for s in strategies_tested.values() if s['status'] == 'healthy')
    total_count = len(strategies_tested)
    
    print(f"Healthy strategies: {{healthy_count}}/{{total_count}}")
    
    for name, info in strategies_tested.items():
        status_icon = "✅" if info['status'] == 'healthy' else "❌"
        print(f"   {{status_icon}} {{name:20}} - {{info['details']}}")
    
    print(f"\\n📋 Project structure check:")
    if os.path.exists("trading_bot/agents/"):
        agent_files = [f for f in os.listdir("trading_bot/agents/") if f.endswith('.py')]
        print(f"   ✅ {{len(agent_files)}} agent files found")
        for f in agent_files:
            print(f"      - {{f}}")
    else:
        print("   ❌ trading_bot/agents/ directory missing")
    
    print("\\n✅ Multi-strategy health check complete!")
    return healthy_count == total_count

check_all_strategies_health()
'''
    subprocess.run(["python3", "-c", script])

def run_docs_update_multi_strategy():
    """Enhanced documentation update with multi-strategy support."""
    print("📚 MULTI-STRATEGY DOCUMENTATION UPDATE")
    print("=" * 50)
    
    script = f'''
import datetime
import os
import sys
sys.path.append('.')

def update_multi_strategy_documentation():
    print("📚 Generating comprehensive strategy documentation...")
    
    # Discover strategies
    strategies = {{}}
    
    try:
        from trading_bot.agents.sma_agent import SMAAgent
        agent = SMAAgent()
        strategies['sma'] = {{
            'name': 'SMA Crossover',
            'description': 'Simple Moving Average crossover strategy',
            'parameters': f'Fast: {{agent.fast_period}}, Slow: {{agent.slow_period}}',
            'status': 'Active'
        }}
    except:
        strategies['sma'] = {{'name': 'SMA Crossover', 'status': 'Error'}}
    
    try:
        from trading_bot.agents.github_agent import GitHubAgent
        strategies['github'] = {{
            'name': 'GitHub AI Strategy',
            'description': 'AI hedge fund strategy from external repo',
            'parameters': 'External strategy integration',
            'status': 'Active'
        }}
    except:
        strategies['github'] = {{'name': 'GitHub AI Strategy', 'status': 'Unavailable'}}
    
    try:
        from trading_bot.agents.optimized_technicals import OptimizedTechnicalAgent
        strategies['technical'] = {{
            'name': 'Optimized Technical',
            'description': 'Multi-indicator technical analysis',
            'parameters': 'Advanced technical indicators',
            'status': 'Active'
        }}
    except:
        strategies['technical'] = {{'name': 'Optimized Technical', 'status': 'Error'}}
    
    # Generate timestamp
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Create comprehensive report
    report_content = f"""# Multi-Strategy Trading Bot Report

Generated: {timestamp}

## Strategy Portfolio Overview

This trading bot supports multiple strategies with automatic discovery and selection capabilities.

### Available Strategies

"""
    
    for key, strategy in strategies.items():
        status_icon = "✅" if strategy['status'] == 'Active' else "❌" if strategy['status'] == 'Error' else "⚠️"
        report_content += f"""#### {status_icon} {strategy['name']}
- **Status**: {strategy['status']}
- **Description**: {strategy.get('description', 'N/A')}
- **Parameters**: {strategy.get('parameters', 'N/A')}

"""
    
    report_content += f"""
## Multi-Strategy Workflow Agents

| Agent | Multi-Strategy Support | Purpose |
|-------|----------------------|---------|
| `smoke-test` | ✅ All strategies | Comprehensive testing |
| `paper-trade-sim` | ✅ Strategy selection | Interactive testing |
| `performance-benchmark` | ✅ All strategies | Performance comparison |
| `agent-health-check` | ✅ All strategies | System validation |
| `quick-backtest` | ✅ Strategy selection | Historical testing |
| `strategy-analyze` | ✅ All strategies | Strategy comparison |
| `dev-setup` | ➖ Environment only | Dependency checking |
| `clean-repo` | ➖ Maintenance only | File cleanup |
| `docs-update` | ✅ All strategies | Documentation generation |

## Access Methods

### Cursor UI
1. **Cmd+Shift+P** → "Tasks: Run Task"
2. Select multi-strategy enabled agents:
   - 🧪 Multi-Strategy Smoke Test
   - 🏃‍♂️ Multi-Strategy Performance Benchmark
   - 🏥 Multi-Strategy Health Check
   - 📚 Multi-Strategy Documentation

### Command Line
```bash
# Multi-strategy agents
python3 run_agent_multi_strategy.py

# Strategy selection demos
python3 test_strategy_selection.py

# Original agents (still work)
python3 run_agent.py
```

## Strategy Performance Summary

Run strategy comparison to get detailed performance metrics:
- Signal frequency analysis
- Buy/sell ratio comparison
- Processing speed benchmarks
- Error rate monitoring

## Development Workflow

1. **Daily Start**: Multi-strategy health check
2. **Development**: Strategy-specific testing
3. **Validation**: Multi-strategy smoke test
4. **Analysis**: Strategy comparison
5. **Documentation**: Auto-generated reports

Generated automatically by multi-strategy docs-update agent.
"""
    
    try:
        with open('MULTI_STRATEGY_REPORT.md', 'w') as f:
            f.write(report_content)
        print("📄 Generated MULTI_STRATEGY_REPORT.md")
        
        # Also update the existing report
        with open('AGENT_PERFORMANCE_REPORT.md', 'w') as f:
            f.write(report_content)
        print("📄 Updated AGENT_PERFORMANCE_REPORT.md")
        
    except Exception as e:
        print(f"❌ Could not write reports: {{e}}")
    
    print("✅ Multi-strategy documentation update complete!")

update_multi_strategy_documentation()
'''
    subprocess.run(["python3", "-c", script])

MULTI_STRATEGY_AGENTS = {
    "smoke-test": ("Multi-Strategy Smoke Test", run_smoke_test_multi_strategy),
    "performance-benchmark": ("Multi-Strategy Performance Benchmark", run_performance_benchmark_multi_strategy),
    "agent-health-check": ("Multi-Strategy Health Check", run_agent_health_check_multi_strategy),
    "docs-update": ("Multi-Strategy Documentation", run_docs_update_multi_strategy),
    # Strategy selection agents from advanced runner
    "paper-trade": ("Paper Trade with Strategy Selection", lambda: subprocess.run(["python3", "test_strategy_selection.py"])),
    "strategy-comparison": ("Strategy Comparison Analysis", lambda: subprocess.run(["python3", "-c", "from test_strategy_selection import test_strategy_comparison; import asyncio; asyncio.run(test_strategy_comparison())"])),
    "backtest": ("Backtest with Strategy Selection", lambda: subprocess.run(["python3", "run_agent_advanced.py", "3"])),
    # Environment agents (don't need strategy selection)
    "dev-setup": ("Development Setup", lambda: subprocess.run(["python3", "run_agent.py", "dev-setup"])),
    "clean-repo": ("Repository Cleanup", lambda: subprocess.run(["python3", "run_agent.py", "clean-repo"]))
}

def show_main_menu():
    """Display main menu for multi-strategy agents."""
    print("🤖 MULTI-STRATEGY TRADING BOT WORKFLOW")
    print("=" * 60)
    print("Enhanced workflow agents with strategy selection:")
    
    for i, (key, (name, _)) in enumerate(MULTI_STRATEGY_AGENTS.items(), 1):
        icon = "🎯" if "Strategy" in name else "🔧" if "Setup" in name or "Cleanup" in name else "📊"
        print(f"  {i:2}. {icon} {name}")
    
    print("   0. Exit")
    print("=" * 60)

def main():
    """Main menu for multi-strategy workflow agents."""
    while True:
        show_main_menu()
        
        try:
            choice = input("\\nSelect agent (1-9) or 0 to exit: ").strip()
            
            if choice == "0":
                print("👋 Goodbye!")
                break
            
            choice_num = int(choice)
            agents_list = list(MULTI_STRATEGY_AGENTS.items())
            
            if 1 <= choice_num <= len(agents_list):
                key, (name, func) = agents_list[choice_num - 1]
                print(f"\\n🚀 Running {name}...")
                print("-" * 50)
                func()
                print("-" * 50)
            else:
                print("❌ Invalid choice. Please try again.")
                
        except (ValueError, KeyboardInterrupt):
            print("❌ Invalid input. Please enter a number.")
        
        input("\\nPress Enter to continue...")

if __name__ == "__main__":
    main()