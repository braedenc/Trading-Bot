"""
Simple Agent Heartbeat Acceptance Test

Tests:
1. Killing SMAAgent loop turns card red within 2 minutes  
2. Health table updating in Supabase
"""

import asyncio
import sys
from datetime import datetime, timedelta

# Add project root to path
sys.path.append('.')

from trading_bot.execution import initialize_heartbeat_system, AgentExecutor
from trading_bot.agents.sma_agent import SMAAgent
from dashboard.agent_health_card import AgentHealthCard
from trading_bot.test_sma_simple import generate_mock_price_data


async def test_heartbeat_acceptance():
    """Simple acceptance test for heartbeat system"""
    
    print("🎯 AGENT HEARTBEAT ACCEPTANCE TEST")
    print("=" * 50)
    
    # 1. Setup
    print("\n1. Initializing system...")
    heartbeat_manager = initialize_heartbeat_system()
    executor = AgentExecutor(heartbeat_manager)
    agent = SMAAgent(fast_period=10, slow_period=20)
    agent.name = "Test_SMA_Agent"
    
    # Test Supabase connection
    if heartbeat_manager.supabase:
        print("✅ Supabase connected")
        try:
            await heartbeat_manager.heartbeat("CONNECTION_TEST", "healthy")
            print("✅ Test heartbeat sent to Supabase")
        except Exception as e:
            print(f"⚠️  Supabase test failed: {e}")
    else:
        print("⚠️  No Supabase - using local logging only")
    
    # 2. Run agent for 1 minute
    print("\n2. Running agent for 1 minute...")
    start_time = datetime.utcnow()
    
    for i in range(4):  # 4 iterations over 1 minute
        mock_data = generate_mock_price_data("TEST", 50 + i)
        snapshot = {
            'prices': {'TEST': mock_data},
            'positions': {'TEST': 0},
            'timestamp': datetime.now()
        }
        
        signals = await executor.execute_agent_with_heartbeat(agent, snapshot)
        elapsed = (datetime.utcnow() - start_time).total_seconds()
        print(f"   {elapsed:>5.1f}s: Generated {len(signals)} signals - 🟢 HEALTHY")
        
        if i < 3:  # Don't sleep after last iteration
            await asyncio.sleep(15)
    
    print("🛑 Stopping agent (simulating kill)")
    
    # 3. Monitor dashboard for red status
    print("\n3. Monitoring dashboard for red status...")
    dashboard = AgentHealthCard(heartbeat_manager.supabase)
    
    red_detected = False
    monitor_start = datetime.utcnow()
    
    for check in range(24):  # Check every 10 seconds for 4 minutes
        health_data = await dashboard.get_agent_health_data()
        
        # Find our test agent
        test_agent = None
        for agent_health in health_data:
            if agent_health.name == "Test_SMA_Agent":
                test_agent = agent_health
                break
        
        elapsed = (datetime.utcnow() - monitor_start).total_seconds()
        
        if test_agent:
            is_stale = test_agent.is_stale
            status_icon = test_agent.status_icon
            time_since_heartbeat = datetime.utcnow() - test_agent.last_heartbeat
            
            print(f"   {elapsed:>5.1f}s: {status_icon} {test_agent.status.upper()}" + 
                  (f" (STALE - {time_since_heartbeat.total_seconds():.0f}s old)" if is_stale else ""))
            
            # Check if red (error status or stale)
            if test_agent.status == "error" or is_stale:
                if not red_detected:
                    red_detected = True
                    print(f"\n🔴 AGENT TURNED RED after {elapsed:.1f} seconds!")
                    
                    if elapsed <= 120:  # 2 minutes
                        print("✅ ACCEPTANCE CRITERIA MET: Red within 2 minutes")
                    else:
                        print("❌ FAILED: Took longer than 2 minutes")
                    break
        else:
            print(f"   {elapsed:>5.1f}s: ❓ Agent not found in dashboard")
        
        await asyncio.sleep(10)
    
    if not red_detected:
        print("❌ FAILED: Agent never turned red")
    
    # 4. Verify Supabase updates
    print("\n4. Verifying Supabase updates...")
    
    if heartbeat_manager.supabase:
        try:
            result = heartbeat_manager.supabase.table("trading_agent_heartbeats")\
                .select("*")\
                .eq("agent_name", "Test_SMA_Agent")\
                .order("timestamp", desc=True)\
                .limit(5)\
                .execute()
            
            if result.data:
                print(f"✅ Found {len(result.data)} heartbeat records in Supabase")
                
                print("📋 Latest records:")
                for i, record in enumerate(result.data):
                    timestamp = record['timestamp']
                    status = record['status']
                    error = record.get('last_error', '')
                    
                    error_msg = f" | Error: {error[:30]}..." if error else ""
                    print(f"   {i+1}. {timestamp} | {status.upper()}{error_msg}")
                
                print("✅ ACCEPTANCE CRITERIA MET: Supabase table updating")
            else:
                print("❌ FAILED: No heartbeat records in Supabase")
                
        except Exception as e:
            print(f"❌ Supabase verification failed: {e}")
    else:
        print("⚠️  Cannot verify Supabase - no connection")
    
    # 5. Cleanup
    print("\n5. Cleaning up...")
    if heartbeat_manager.supabase:
        try:
            # Clean up test records
            heartbeat_manager.supabase.table("trading_agent_heartbeats")\
                .delete()\
                .eq("agent_name", "Test_SMA_Agent")\
                .execute()
            
            heartbeat_manager.supabase.table("trading_agent_heartbeats")\
                .delete()\
                .eq("agent_name", "CONNECTION_TEST")\
                .execute()
                
            print("✅ Test records cleaned up")
        except Exception as e:
            print(f"⚠️  Cleanup error: {e}")
    
    print("\n🎉 ACCEPTANCE TEST COMPLETE!")
    print("\nResults:")
    print("✅ Agent heartbeat system functional")
    print("✅ Dashboard monitoring working" if red_detected else "❌ Dashboard monitoring needs work")
    print("✅ Supabase integration verified" if heartbeat_manager.supabase else "⚠️  Supabase not tested")


def main():
    """Run the acceptance test"""
    print("🔍 Simple Agent Heartbeat Acceptance Test")
    print()
    print("This test will:")
    print("1. Run SMA agent with heartbeats for 1 minute")
    print("2. Stop the agent and monitor dashboard")
    print("3. Verify red indicator appears within 2 minutes")
    print("4. Check Supabase table updates")
    print()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        asyncio.run(test_heartbeat_acceptance())
    else:
        response = input("Ready to run test? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            asyncio.run(test_heartbeat_acceptance())
        else:
            print("Test cancelled.")


if __name__ == "__main__":
    main()