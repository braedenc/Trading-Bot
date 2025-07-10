"""
Agent Heartbeat System Demo
Demonstrates the agent heartbeat functionality with SMA agent
"""

import asyncio
import logging
from datetime import datetime
import sys
import os

# Add project root to path
sys.path.append('.')

from trading_bot.execution import initialize_heartbeat_system, AgentExecutor
from trading_bot.agents.sma_agent import SMAAgent
from dashboard.agent_health_card import show_agent_health
from trading_bot.test_sma_simple import generate_mock_price_data


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def demo_heartbeat_system():
    """Demonstrate the agent heartbeat system"""
    print("🚀 AGENT HEARTBEAT SYSTEM DEMO")
    print("=" * 50)
    
    # Initialize heartbeat system (without real Supabase for demo)
    print("\n1. Initializing heartbeat system...")
    heartbeat_manager = initialize_heartbeat_system()
    executor = AgentExecutor(heartbeat_manager)
    
    # Create agents
    print("\n2. Creating agents...")
    healthy_agent = SMAAgent(fast_period=10, slow_period=20)
    healthy_agent.name = "Healthy_SMA_Agent"
    
    # Create a mock "failing" agent by patching its generate_signals method
    failing_agent = SMAAgent(fast_period=5, slow_period=15)
    failing_agent.name = "Failing_SMA_Agent"
    
    # Override generate_signals to simulate failure
    original_generate_signals = failing_agent.generate_signals
    
    async def failing_generate_signals(snapshot):
        await asyncio.sleep(0.1)  # Simulate some work
        raise ValueError("Simulated agent failure for demo")
    
    failing_agent.generate_signals = failing_generate_signals
    
    # Create test data
    print("\n3. Generating test market data...")
    mock_data = generate_mock_price_data("DEMO", 100)
    
    snapshot = {
        'prices': {'DEMO': mock_data},
        'positions': {'DEMO': 0},
        'timestamp': datetime.now()
    }
    
    # Execute healthy agent
    print("\n4. Executing healthy agent...")
    healthy_signals = await executor.execute_agent_with_heartbeat(healthy_agent, snapshot)
    print(f"   ✅ Healthy agent generated {len(healthy_signals)} signals")
    
    # Execute failing agent (should handle gracefully)
    print("\n5. Executing failing agent...")
    failing_signals = await executor.execute_agent_with_heartbeat(failing_agent, snapshot)
    print(f"   ❌ Failing agent generated {len(failing_signals)} signals (expected 0)")
    
    # Execute multiple agents in parallel
    print("\n6. Executing multiple agents in parallel...")
    from typing import List
    from trading_bot.base_agent import BaseAgent
    all_agents: List[BaseAgent] = [healthy_agent, failing_agent]
    all_results = await executor.execute_multiple_agents(all_agents, snapshot)
    
    print("   📊 Results summary:")
    for agent_name, signals in all_results.items():
        print(f"      {agent_name}: {len(signals)} signals")
    
    # Wait a moment for heartbeats to settle
    await asyncio.sleep(1)
    
    # Display health dashboard
    print("\n7. Displaying agent health dashboard...")
    await show_agent_health()
    
    print("\n8. Manual heartbeat testing...")
    from trading_bot.execution import heartbeat
    
    # Send some manual heartbeats
    await heartbeat("Manual_Test_Agent", "healthy", metadata={"test": True})
    await heartbeat("Manual_Test_Agent", "warning", "Test warning message")
    await heartbeat("Manual_Test_Agent", "error", "Test error message")
    
    print("   ✅ Manual heartbeats sent")
    
    print("\n🎉 Demo completed successfully!")
    print("\nKey Features Demonstrated:")
    print("  ✅ Automatic heartbeat recording during agent execution")
    print("  ✅ Exception handling with error heartbeats")
    print("  ✅ Parallel agent execution with individual heartbeat tracking")
    print("  ✅ Dashboard display of agent health status")
    print("  ✅ Manual heartbeat recording")
    print("\nIn a real deployment:")
    print("  - Set SUPABASE_URL and SUPABASE_ANON_KEY environment variables")
    print("  - Heartbeats will be stored in Supabase database")
    print("  - Dashboard can query real-time agent health data")


async def demo_dashboard_only():
    """Demo just the dashboard component"""
    print("🏥 AGENT HEALTH DASHBOARD DEMO")
    print("=" * 40)
    print("(Using mock data since no real agents are running)")
    print()
    
    await show_agent_health()


async def demo_sma_agent_with_heartbeat():
    """Demo SMA agent with integrated heartbeat"""
    print("📈 SMA AGENT WITH HEARTBEAT DEMO")
    print("=" * 40)
    
    # Create agent
    agent = SMAAgent(fast_period=10, slow_period=20)
    
    # Create test data
    mock_data = generate_mock_price_data("HEARTBEAT_TEST", 50)
    snapshot = {
        'prices': {'HEARTBEAT_TEST': mock_data},
        'positions': {'HEARTBEAT_TEST': 0},
        'timestamp': datetime.now()
    }
    
    print("Executing SMA agent with heartbeat integration...")
    signals = await agent.generate_signals(snapshot)
    
    print(f"✅ Agent executed successfully")
    print(f"📊 Generated {len(signals)} signals")
    
    if signals:
        print("📋 Signals:")
        for signal in signals:
            print(f"   {signal['action'].upper()}: {signal['quantity']:.2f} {signal['symbol']}")
            print(f"   Confidence: {signal['confidence']:.1%}")
    else:
        print("   No signals generated (normal for demo data)")


def main():
    """Main demo entry point"""
    if len(sys.argv) > 1:
        demo_type = sys.argv[1]
    else:
        print("Available demos:")
        print("1. full        - Complete heartbeat system demo")
        print("2. dashboard   - Dashboard component only")
        print("3. sma         - SMA agent with heartbeat")
        print()
        choice = input("Select demo (1-3): ").strip()
        demo_type = {"1": "full", "2": "dashboard", "3": "sma"}.get(choice, "full")
    
    if demo_type == "dashboard":
        asyncio.run(demo_dashboard_only())
    elif demo_type == "sma":
        asyncio.run(demo_sma_agent_with_heartbeat())
    else:
        asyncio.run(demo_heartbeat_system())


if __name__ == "__main__":
    main()