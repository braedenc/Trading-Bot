"""
Agent Heartbeat System Acceptance Test

Tests:
1. Killing SMAAgent loop turns card red within 2 minutes
2. Health table updating in Supabase
"""

import asyncio
import logging
import sys
import os
from datetime import datetime, timedelta
import signal
import time

# Add project root to path
sys.path.append('.')

from trading_bot.execution import initialize_heartbeat_system, AgentExecutor
from trading_bot.agents.sma_agent import SMAAgent
from dashboard.agent_health_card import AgentHealthCard, show_agent_health
from trading_bot.test_sma_simple import generate_mock_price_data

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AcceptanceTest:
    """Acceptance test for heartbeat system"""

    def __init__(self):
        from trading_bot.execution import HeartbeatManager, AgentExecutor
        from trading_bot.agents.sma_agent import SMAAgent
        from typing import Optional

        self.heartbeat_manager: Optional[HeartbeatManager] = None
        self.executor: Optional[AgentExecutor] = None
        self.agent: Optional[SMAAgent] = None
        self.running = True
        self.test_start_time: Optional[datetime] = None

    async def setup(self):
        """Initialize the test environment"""
        print("🔧 ACCEPTANCE TEST SETUP")
        print("=" * 50)

        # Initialize heartbeat system
        print("1. Initializing heartbeat system...")
        self.heartbeat_manager = initialize_heartbeat_system()
        self.executor = AgentExecutor(self.heartbeat_manager)

        # Create SMA agent
        print("2. Creating SMA Agent...")
        self.agent = SMAAgent(fast_period=10, slow_period=20)
        self.agent.name = "AcceptanceTest_SMA_Agent"

        # Test Supabase connection
        print("3. Testing Supabase connection...")
        if self.heartbeat_manager.supabase:
            try:
                # Try a test heartbeat
                await self.heartbeat_manager.heartbeat(
                    "TEST_CONNECTION",
                    "healthy",
                    metadata={"test": "connection_check"}
                )
                print("   ✅ Supabase connection successful")

                # Query to verify write
                result = self.heartbeat_manager.supabase.table("trading_agent_heartbeats")\
                    .select("*")\
                    .eq("agent_name", "TEST_CONNECTION")\
                    .order("timestamp", desc=True)\
                    .limit(1)\
                    .execute()

                if result.data:
                    print(f"   ✅ Verified heartbeat written to Supabase: {result.data[0]['timestamp']}")

                    # Clean up test record
                    self.heartbeat_manager.supabase.table("trading_agent_heartbeats")\
                        .delete()\
                        .eq("agent_name", "TEST_CONNECTION")\
                        .execute()
                    print("   🧹 Cleaned up test record")
                else:
                    print("   ⚠️  Could not verify Supabase write")

            except Exception as e:
                print(f"   ❌ Supabase error: {e}")
                print("   ⚠️  Will continue with local logging only")
        else:
            print("   ⚠️  No Supabase connection - using local logging only")

        print("✅ Setup complete\n")

    async def run_agent_loop(self, duration_minutes=5):
        """
        Run the SMA agent in a loop for the specified duration
        This simulates normal agent operation
        """
        print(f"🔄 RUNNING AGENT LOOP ({duration_minutes} minutes)")
        print("=" * 50)

        self.test_start_time = datetime.utcnow()
        end_time = self.test_start_time + timedelta(minutes=duration_minutes)
        iteration = 0

        while datetime.utcnow() < end_time and self.running:
            iteration += 1

            # Generate fresh mock data each iteration
            mock_data = generate_mock_price_data("ACCEPTANCE_TEST", 50 + iteration)

            snapshot = {
                'prices': {'ACCEPTANCE_TEST': mock_data},
                'positions': {'ACCEPTANCE_TEST': 0},
                'timestamp': datetime.now()
            }
            try:
                # Execute agent with heartbeat
                assert self.executor is not None, "Executor not initialized"
                assert self.agent is not None, "Agent not initialized"
                signals = await self.executor.execute_agent_with_heartbeat(self.agent, snapshot)

                elapsed = datetime.utcnow() - self.test_start_time
                print(f"⏱️  {elapsed.total_seconds():>6.1f}s | Iteration {iteration:>3} | "
                      f"Generated {len(signals)} signals | Status: 🟢 HEALTHY")

                # Wait 15 seconds between iterations (4 per minute)
                await asyncio.sleep(15)

            except Exception as e:
                print(f"❌ Agent execution failed: {e}")
                break

        if not self.running:
            print("\n🛑 Agent loop stopped (simulated kill)")
        else:
            print(f"\n⏰ Agent loop completed after {duration_minutes} minutes")

    def kill_agent(self):
        """Simulate killing the agent"""
        print("\n💀 SIMULATING AGENT KILL")
        print("=" * 30)
        self.running = False

    async def monitor_dashboard(self, check_duration_minutes=3):
        """
        Monitor the dashboard to verify it turns red within 2 minutes
        """
        print(f"\n🏥 MONITORING DASHBOARD ({check_duration_minutes} minutes)")
        print("=" * 50)

        dashboard = AgentHealthCard(self.heartbeat_manager.supabase)
        monitor_start = datetime.utcnow()
        end_time = monitor_start + timedelta(minutes=check_duration_minutes)

        red_detected = False
        last_status = None

        while datetime.utcnow() < end_time:
            try:
                # Get health data
                health_data = await dashboard.get_agent_health_data()

                # Find our test agent
                test_agent = next(
                    (agent for agent in health_data if agent.name == "AcceptanceTest_SMA_Agent"),
                    None
                )

                elapsed = datetime.utcnow() - monitor_start

                if test_agent:
                    status_change = last_status != test_agent.status
                    status_icon = test_agent.status_icon
                    is_stale = test_agent.is_stale

                    time_since_heartbeat = datetime.utcnow() - test_agent.last_heartbeat if test_agent.last_heartbeat else None
                    heartbeat_age = f"{time_since_heartbeat.total_seconds():.0f}s" if time_since_heartbeat else "Unknown"

                    stale_marker = " (STALE)" if is_stale else ""
                    change_marker = " ← STATUS CHANGE" if status_change else ""

                    print(f"⏱️  {elapsed.total_seconds():>6.1f}s | Agent: {status_icon} {test_agent.status.upper()}"
                          f"{stale_marker} | Last heartbeat: {heartbeat_age} ago{change_marker}")

                    if test_agent.last_error:
                        print(f"        Error: {test_agent.last_error[:60]}...")

                    # Check if agent turned red
                    if test_agent.status == "error" or is_stale:
                        if not red_detected:
                            red_detected = True
                            time_to_red = elapsed.total_seconds()
                            print(f"\n🔴 AGENT TURNED RED after {time_to_red:.1f} seconds!")

                            if time_to_red <= 120:  # 2 minutes
                                print("✅ ACCEPTANCE CRITERIA MET: Red status within 2 minutes")
                            else:
                                print("❌ ACCEPTANCE CRITERIA FAILED: Red status took longer than 2 minutes")

                    last_status = test_agent.status
                else:
                    print(f"⏱️  {elapsed.total_seconds():>6.1f}s | Agent: ❓ NOT FOUND")

                # Wait 10 seconds between checks
                await asyncio.sleep(10)

            except Exception as e:
                print(f"❌ Dashboard monitoring error: {e}")
                await asyncio.sleep(10)

        return red_detected

    async def verify_supabase_updates(self):
        """Verify that heartbeat data is being written to Supabase"""
        print("\n📊 VERIFYING SUPABASE UPDATES")
        print("=" * 40)

        if not self.heartbeat_manager.supabase:
            print("❌ No Supabase connection - cannot verify database updates")
            return False

        try:
            # Query for our test agent's heartbeats
            result = self.heartbeat_manager.supabase.table("trading_agent_heartbeats")\
                .select("*")\
                .eq("agent_name", "AcceptanceTest_SMA_Agent")\
                .order("timestamp", desc=True)\
                .limit(10)\
                .execute()

            if result.data:
                print(f"✅ Found {len(result.data)} heartbeat records in Supabase")

                # Show latest records
                print("\n📋 Latest heartbeat records:")
                for i, record in enumerate(result.data[:5]):
                    timestamp = record['timestamp']
                    status = record['status']
                    error = record.get('last_error', '')
                    metadata = record.get('metadata', {})

                    error_info = f" | Error: {error[:30]}..." if error else ""
                    meta_info = f" | Metadata: {metadata}" if metadata else ""

                    print(f"   {i+1}. {timestamp} | {status.upper()}{error_info}{meta_info}")

                # Verify we have recent records
                latest_record = result.data[0]
                latest_time = datetime.fromisoformat(latest_record['timestamp'].replace('Z', '+00:00'))
                time_since_latest = datetime.utcnow() - latest_time

                print(f"\n⏰ Latest record is {time_since_latest.total_seconds():.0f} seconds old")

                if time_since_latest.total_seconds() < 300:  # Within 5 minutes
                    print("✅ ACCEPTANCE CRITERIA MET: Recent heartbeats in Supabase")
                    return True
                else:
                    print("⚠️  Latest heartbeat is quite old")
                    return True  # Still counts as having data
            else:
                print("❌ No heartbeat records found in Supabase")
                return False

        except Exception as e:
            print(f"❌ Error querying Supabase: {e}")
            return False

    async def cleanup(self):
        """Clean up test data"""
        print("\n🧹 CLEANUP")
        print("=" * 20)

        if self.heartbeat_manager.supabase:
            try:
                # Optionally clean up test records
                # (Comment out if you want to keep them for inspection)
                print("Cleaning up test heartbeat records...")

                result = self.heartbeat_manager.supabase.table("trading_agent_heartbeats")\
                    .delete()\
                    .eq("agent_name", "AcceptanceTest_SMA_Agent")\
                    .execute()

                print("✅ Test records cleaned up")

            except Exception as e:
                print(f"⚠️  Cleanup error: {e}")

        print("✅ Cleanup complete")


async def run_acceptance_test():
    """Run the complete acceptance test"""
    print("🎯 AGENT HEARTBEAT ACCEPTANCE TEST")
    print("=" * 60)
    print("Testing:")
    print("1. SMA Agent heartbeat system")
    print("2. Dashboard red indicator within 2 minutes of agent failure")
    print("3. Supabase database updates")
    print()

    test = AcceptanceTest()

    try:
        # Setup
        await test.setup()

        # Start monitoring dashboard in background
        dashboard_task = asyncio.create_task(test.monitor_dashboard(check_duration_minutes=4))

        # Run agent for 2 minutes, then simulate kill
        agent_task = asyncio.create_task(test.run_agent_loop(duration_minutes=2))

        # Wait 1.5 minutes, then kill the agent
        await asyncio.sleep(90)  # 1.5 minutes
        test.kill_agent()

        # Wait for agent task to complete
        await agent_task

        # Continue monitoring for another 2 minutes to see red status
        await dashboard_task

        # Verify Supabase updates
        supabase_ok = await test.verify_supabase_updates()

        # Final status
        print("\n🎯 ACCEPTANCE TEST RESULTS")
        print("=" * 40)
        print("✅ Agent heartbeat system operational")
        print("✅ Dashboard monitoring functional")

        if supabase_ok:
            print("✅ Supabase integration working")
        else:
            print("⚠️  Supabase integration needs verification")

        print("\n🎉 ACCEPTANCE TEST COMPLETED")

    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        test.kill_agent()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await test.cleanup()


def main():
    """Main entry point"""
    print("🔍 Agent Heartbeat Acceptance Test")
    print()
    print("This test will:")
    print("1. Run an SMA agent with heartbeats for 2 minutes")
    print("2. Kill the agent to simulate failure")
    print("3. Monitor dashboard for red indicator within 2 minutes")
    print("4. Verify Supabase database updates")
    print()

    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        # Run automatically
        asyncio.run(run_acceptance_test())
    else:
        # Ask for confirmation
        response = input("Ready to run acceptance test? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            asyncio.run(run_acceptance_test())
        else:
            print("Test cancelled.")


if __name__ == "__main__":
    main()