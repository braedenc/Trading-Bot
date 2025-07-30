"""
Unit tests for agent heartbeat system
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
import json

# Import the modules to test
from trading_bot.execution import HeartbeatManager, AgentExecutor, heartbeat
from trading_bot.agents.sma_agent import SMAAgent
from dashboard.agent_health_card import AgentHealthCard, AgentHealth


class TestHeartbeatManager:
    """Test the HeartbeatManager class"""

    def test_heartbeat_manager_init_no_supabase(self):
        """Test initialization without Supabase credentials"""
        manager = HeartbeatManager()
        assert manager.supabase is None

    def test_heartbeat_manager_init_with_mock_supabase(self):
        """Test initialization with Supabase credentials"""
        with patch('trading_bot.execution.HAS_SUPABASE', True):
            with patch('trading_bot.execution.create_client') as mock_create:
                mock_client = Mock()
                mock_create.return_value = mock_client

                manager = HeartbeatManager("http://test.supabase.co", "test-key")
                assert manager.supabase == mock_client
                mock_create.assert_called_once_with("http://test.supabase.co", "test-key")

    @pytest.mark.asyncio
    async def test_heartbeat_logging_only(self):
        """Test heartbeat logging when Supabase is not available"""
        manager = HeartbeatManager()

        # Should return True even without Supabase
        result = await manager.heartbeat("test_agent", "healthy")
        assert result is True

    @pytest.mark.asyncio
    async def test_heartbeat_with_mock_supabase(self):
        """Test heartbeat with mocked Supabase client"""
        mock_client = Mock()
        mock_table = Mock()
        mock_client.table.return_value = mock_table
        mock_table.insert.return_value = mock_table
        mock_table.execute.return_value = Mock()

        manager = HeartbeatManager()
        manager.supabase = mock_client

        result = await manager.heartbeat(
            "test_agent",
            "healthy",
            metadata={"test": "data"}
        )

        assert result is True
        mock_client.table.assert_called_once_with("trading_agent_heartbeats")
        mock_table.insert.assert_called_once()
        mock_table.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_heartbeat_supabase_error(self):
        """Test heartbeat when Supabase throws an error"""
        mock_client = Mock()
        mock_client.table.side_effect = Exception("Database error")

        manager = HeartbeatManager()
        manager.supabase = mock_client

        result = await manager.heartbeat("test_agent", "error", "Test error")

        # Should return False when Supabase fails but still log locally
        assert result is False


class TestAgentExecutor:
    """Test the AgentExecutor class"""

    def setup_method(self):
        """Set up test fixtures"""
        self.heartbeat_manager = HeartbeatManager()
        self.executor = AgentExecutor(self.heartbeat_manager)

    @pytest.mark.asyncio
    async def test_execute_healthy_agent(self):
        """Test executing a healthy agent"""
        # Create a mock agent
        mock_agent = Mock(spec=SMAAgent)
        mock_agent.name = "TestAgent"
        mock_agent.generate_signals = AsyncMock(return_value=[
            {"symbol": "AAPL", "action": "buy", "quantity": 100}
        ])

        snapshot = {"prices": {"AAPL": {"close": 150.0}}}

        # Mock the heartbeat manager
        with patch.object(self.heartbeat_manager, 'heartbeat', new_callable=AsyncMock) as mock_heartbeat:
            signals = await self.executor.execute_agent_with_heartbeat(mock_agent, snapshot)

            # Should return the signals
            assert len(signals) == 1
            assert signals[0]["symbol"] == "AAPL"

            # Should have called heartbeat twice (start and success)
            assert mock_heartbeat.call_count == 2

            # Check heartbeat calls
            calls = mock_heartbeat.call_args_list
            assert calls[0][0][0] == "TestAgent"  # agent name
            assert calls[0][0][1] == "healthy"    # status
            assert calls[1][0][1] == "healthy"    # final status

    @pytest.mark.asyncio
    async def test_execute_failing_agent(self):
        """Test executing an agent that throws an exception"""
        # Create a mock agent that raises an exception
        mock_agent = Mock(spec=SMAAgent)
        mock_agent.name = "FailingAgent"
        mock_agent.generate_signals = AsyncMock(side_effect=ValueError("Test error"))

        snapshot = {"prices": {"AAPL": {"close": 150.0}}}

        # Mock the heartbeat manager
        with patch.object(self.heartbeat_manager, 'heartbeat', new_callable=AsyncMock) as mock_heartbeat:
            signals = await self.executor.execute_agent_with_heartbeat(mock_agent, snapshot)

            # Should return empty signals list
            assert signals == []

            # Should have called heartbeat twice (start and error)
            assert mock_heartbeat.call_count == 2

            # Check error heartbeat
            calls = mock_heartbeat.call_args_list
            assert calls[1][0][1] == "error"  # status should be error
            assert "ValueError: Test error" in calls[1][0][2]

    @pytest.mark.asyncio
    async def test_execute_multiple_agents(self):
        """Test executing multiple agents in parallel"""
        # Create mock agents
        agent1 = Mock(spec=SMAAgent)
        agent1.name = "Agent1"
        agent1.generate_signals = AsyncMock(return_value=[{"signal": "buy"}])

        agent2 = Mock(spec=SMAAgent)
        agent2.name = "Agent2"
        agent2.generate_signals = AsyncMock(return_value=[{"signal": "sell"}])

        snapshot = {"prices": {"AAPL": {"close": 150.0}}}

        with patch.object(self.executor, 'execute_agent_with_heartbeat', new_callable=AsyncMock) as mock_execute:
            mock_execute.side_effect = [
                [{"signal": "buy"}],   # Agent1 result
                [{"signal": "sell"}]   # Agent2 result
            ]

            results = await self.executor.execute_multiple_agents([agent1, agent2], snapshot)

            assert "Agent1" in results
            assert "Agent2" in results
            assert len(results["Agent1"]) == 1
            assert len(results["Agent2"]) == 1


class TestSMAAgentHeartbeat:
    """Test SMA Agent heartbeat integration"""

    @pytest.mark.asyncio
    async def test_sma_agent_with_heartbeat(self):
        """Test SMA agent executes heartbeats during signal generation"""
        agent = SMAAgent(fast_period=5, slow_period=10)

        # Create mock data
        mock_data = {
            "historical": [
                {"timestamp": "2024-01-01T10:00:00Z", "close": 100.0},
                {"timestamp": "2024-01-01T10:01:00Z", "close": 101.0},
                {"timestamp": "2024-01-01T10:02:00Z", "close": 102.0},
                # Not enough data for SMA calculation
            ]
        }

        snapshot = {
            "prices": {"TEST": mock_data},
            "positions": {"TEST": 0}
        }

        # Mock the heartbeat function
        with patch('trading_bot.execution.heartbeat', new_callable=AsyncMock) as mock_heartbeat:
            signals = await agent.generate_signals(snapshot)

            # Heartbeat should have been called
            assert mock_heartbeat.call_count >= 1

            # Check that agent name was passed correctly
            calls = mock_heartbeat.call_args_list
            assert calls[0][0][0] == "SMA_Agent"  # agent name


class TestAgentHealthCard:
    """Test the AgentHealthCard dashboard component"""

    def test_agent_health_creation(self):
        """Test creating AgentHealth objects"""
        health = AgentHealth(
            name="TestAgent",
            status="healthy",
            last_heartbeat=datetime.utcnow()
        )

        assert health.name == "TestAgent"
        assert health.status == "healthy"
        assert health.status_color == "green"
        assert health.status_icon == "🟢"
        assert not health.is_stale

    def test_agent_health_stale_detection(self):
        """Test stale heartbeat detection"""
        old_time = datetime.utcnow() - timedelta(minutes=10)
        health = AgentHealth(
            name="TestAgent",
            status="healthy",
            last_heartbeat=old_time
        )

        assert health.is_stale

    @pytest.mark.asyncio
    async def test_health_card_mock_data(self):
        """Test health card with mock data"""
        card = AgentHealthCard()
        health_data = await card.get_agent_health_data()

        # Should return mock data
        assert len(health_data) >= 1
        assert any(agent.name == "SMA_Agent" for agent in health_data)

    def test_health_card_console_render(self):
        """Test console rendering of health data"""
        card = AgentHealthCard()
        health_data = [
            AgentHealth(
                name="TestAgent",
                status="healthy",
                last_heartbeat=datetime.utcnow(),
                metadata={"signals_generated": 5}
            )
        ]

        output = card.render_console_view(health_data)

        assert "AGENT HEALTH DASHBOARD" in output
        assert "TestAgent" in output
        assert "HEALTHY" in output
        assert "Signals: 5" in output

    def test_health_summary(self):
        """Test health summary generation"""
        card = AgentHealthCard()
        health_data = [
            AgentHealth("Agent1", "healthy", datetime.utcnow()),
            AgentHealth("Agent2", "warning", datetime.utcnow(), "Test warning"),
            AgentHealth("Agent3", "error", datetime.utcnow(), "Test error")
        ]

        summary = card.get_health_summary(health_data)

        assert summary["total_agents"] == 3
        assert summary["healthy"] == 1
        assert summary["warning"] == 1
        assert summary["error"] == 1
        assert len(summary["agents"]) == 3


class TestGlobalHeartbeatFunction:
    """Test the global heartbeat convenience function"""

    @pytest.mark.asyncio
    async def test_global_heartbeat_function(self):
        """Test the global heartbeat function"""
        with patch('trading_bot.execution.get_heartbeat_manager') as mock_get_manager:
            mock_manager = Mock()
            mock_manager.heartbeat = AsyncMock(return_value=True)
            mock_get_manager.return_value = mock_manager

            result = await heartbeat("test_agent", "healthy")

            assert result is True
            mock_manager.heartbeat.assert_called_once_with("test_agent", "healthy", None, None)


# Integration test
class TestHeartbeatIntegration:
    """Integration tests for the complete heartbeat system"""

    @pytest.mark.asyncio
    async def test_end_to_end_heartbeat_flow(self):
        """Test complete flow from agent execution to dashboard display"""
        # Initialize components
        heartbeat_manager = HeartbeatManager()
        executor = AgentExecutor(heartbeat_manager)

        # Create a real SMA agent
        agent = SMAAgent(fast_period=5, slow_period=10)

        # Create test data (insufficient for signals)
        snapshot = {
            "prices": {
                "TEST": {
                    "historical": [
                        {"timestamp": "2024-01-01T10:00:00Z", "close": 100.0}
                    ]
                }
            },
            "positions": {"TEST": 0}
        }

        # Execute agent
        signals = await executor.execute_agent_with_heartbeat(agent, snapshot)

        # Should complete without errors
        assert isinstance(signals, list)

        # Test dashboard rendering
        dashboard = AgentHealthCard()
        health_data = await dashboard.get_agent_health_data()

        # Should get mock data since no real Supabase
        assert len(health_data) > 0


if __name__ == "__main__":
    # Run basic tests
    pytest.main([__file__, "-v"])