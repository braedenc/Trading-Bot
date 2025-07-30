"""
Agent Health Card Dashboard Component
Shows green/yellow/red indicator for agent status
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import json

# Optional rich console for better formatting
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    HAS_RICH = True
except ImportError:
    HAS_RICH = False


@dataclass
class AgentHealth:
    """Agent health status data"""
    name: str
    status: str  # 'healthy', 'warning', 'error'
    last_heartbeat: datetime
    last_error: Optional[str] = None
    metadata: Optional[Dict] = None

    @property
    def status_color(self) -> str:
        """Get color for status"""
        return {
            'healthy': 'green',
            'warning': 'yellow',
            'error': 'red'
        }.get(self.status, 'gray')

    @property
    def status_icon(self) -> str:
        """Get emoji icon for status"""
        return {
            'healthy': '🟢',
            'warning': '🟡',
            'error': '🔴'
        }.get(self.status, '⚪')

    @property
    def is_stale(self) -> bool:
        """Check if heartbeat is stale (>5 minutes old)"""
        if not self.last_heartbeat:
            return True
        return datetime.utcnow() - self.last_heartbeat > timedelta(minutes=5)


class AgentHealthCard:
    """Dashboard component for displaying agent health"""

    def __init__(self, supabase_client=None):
        self.supabase = supabase_client
        self.console = Console() if HAS_RICH else None
        self._cached_health = {}
        self._cache_ttl = timedelta(seconds=30)  # Cache for 30 seconds
        self._last_cache_update = None

    async def get_agent_health_data(self) -> List[AgentHealth]:
        """
        Fetch agent health data from Supabase or return mock data
        """
        # Use cache if recent
        now = datetime.utcnow()
        if (self._last_cache_update and
            now - self._last_cache_update < self._cache_ttl and
            self._cached_health):
            return list(self._cached_health.values())

        health_data = []

        if self.supabase:
            try:
                # Fetch latest heartbeat for each agent
                result = self.supabase.from_("agent_health_latest").select("*").execute()

                for row in result.data:
                    health = AgentHealth(
                        name=row['agent_name'],
                        status=row['status'],
                        last_heartbeat=datetime.fromisoformat(row['timestamp'].replace('Z', '+00:00')),
                        last_error=row.get('last_error'),
                        metadata=row.get('metadata', {})
                    )
                    health_data.append(health)
                    self._cached_health[health.name] = health

                self._last_cache_update = now

            except Exception as e:
                print(f"❌ Error fetching agent health from Supabase: {e}")
                # Fall back to mock data
                health_data = self._get_mock_health_data()
        else:
            # Use mock data when Supabase is not available
            health_data = self._get_mock_health_data()

        return health_data

    def _get_mock_health_data(self) -> List[AgentHealth]:
        """Generate mock health data for testing"""
        mock_agents = [
            AgentHealth(
                name="SMA_Agent",
                status="healthy",
                last_heartbeat=datetime.utcnow() - timedelta(seconds=30),
                metadata={"signals_generated": 3, "symbols_processed": 5}
            ),
            AgentHealth(
                name="RSI_Agent",
                status="warning",
                last_heartbeat=datetime.utcnow() - timedelta(minutes=2),
                last_error="Timeout processing AAPL data",
                metadata={"symbols_processed": 3}
            ),
            AgentHealth(
                name="MACD_Agent",
                status="error",
                last_heartbeat=datetime.utcnow() - timedelta(minutes=10),
                last_error="Division by zero in signal calculation",
                metadata={"error_type": "ZeroDivisionError"}
            )
        ]
        return mock_agents

    def render_console_view(self, health_data: List[AgentHealth]) -> str:
        """Render health data for console output"""
        if not health_data:
            return "No agent health data available"

        output = []
        output.append("🏥 AGENT HEALTH DASHBOARD")
        output.append("=" * 40)

        for agent in health_data:
            time_since = datetime.utcnow() - agent.last_heartbeat if agent.last_heartbeat else None
            time_str = f"{time_since.total_seconds():.0f}s ago" if time_since else "Unknown"

            status_line = f"{agent.status_icon} {agent.name:<15} | {agent.status.upper():<8} | {time_str}"

            if agent.is_stale:
                status_line += " ⚠️  STALE"

            output.append(status_line)

            if agent.last_error:
                output.append(f"   ❌ Error: {agent.last_error[:60]}...")

            if agent.metadata and isinstance(agent.metadata, dict):
                if 'signals_generated' in agent.metadata:
                    output.append(f"   📊 Signals: {agent.metadata['signals_generated']}")

        output.append("")
        output.append(f"Updated: {datetime.utcnow().strftime('%H:%M:%S UTC')}")

        return "\n".join(output)

    def render_rich_view(self, health_data: List[AgentHealth]) -> None:
        """Render health data using Rich formatting"""
        if not self.console:
            print(self.render_console_view(health_data))
            return

        table = Table(title="🏥 Agent Health Dashboard")
        table.add_column("Agent", style="bold")
        table.add_column("Status", justify="center")
        table.add_column("Last Heartbeat", justify="center")
        table.add_column("Details", style="dim")

        for agent in health_data:
            time_since = datetime.utcnow() - agent.last_heartbeat if agent.last_heartbeat else None
            time_str = f"{time_since.total_seconds():.0f}s ago" if time_since else "Unknown"

            status_text = Text(f"{agent.status_icon} {agent.status.upper()}")
            status_text.stylize(agent.status_color)

            if agent.is_stale:
                time_str += " ⚠️"

            details = []
            if agent.last_error:
                details.append(f"Error: {agent.last_error[:40]}...")
            if agent.metadata and 'signals_generated' in agent.metadata:
                details.append(f"Signals: {agent.metadata['signals_generated']}")

            table.add_row(
                agent.name,
                status_text,
                time_str,
                "\n".join(details)
            )

        panel = Panel(table, title="Trading Bot Agent Health", border_style="blue")
        self.console.print(panel)

    async def display_health_dashboard(self, use_rich: bool = True) -> None:
        """Display the agent health dashboard"""
        health_data = await self.get_agent_health_data()

        if use_rich and HAS_RICH:
            self.render_rich_view(health_data)
        else:
            print(self.render_console_view(health_data))

    def get_health_summary(self, health_data: Optional[List[AgentHealth]] = None) -> Dict[str, Any]:
        """Get a summary of agent health for API/JSON consumption"""
        if health_data is None:
            # This would need to be called with asyncio.run in a sync context
            return {"error": "Cannot fetch data synchronously"}

        summary = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_agents": len(health_data),
            "healthy": len([a for a in health_data if a.status == "healthy"]),
            "warning": len([a for a in health_data if a.status == "warning"]),
            "error": len([a for a in health_data if a.status == "error"]),
            "stale": len([a for a in health_data if a.is_stale]),
            "agents": [
                {
                    "name": agent.name,
                    "status": agent.status,
                    "last_heartbeat": agent.last_heartbeat.isoformat() if agent.last_heartbeat else None,
                    "last_error": agent.last_error,
                    "is_stale": agent.is_stale,
                    "metadata": agent.metadata
                }
                for agent in health_data
            ]
        }

        return summary


# Convenience functions
async def show_agent_health(supabase_client=None):
    """Quick function to display agent health dashboard"""
    dashboard = AgentHealthCard(supabase_client)
    await dashboard.display_health_dashboard()

def create_health_card(supabase_client=None) -> AgentHealthCard:
    """Factory function to create AgentHealthCard"""
    return AgentHealthCard(supabase_client)


# CLI entry point for testing
if __name__ == "__main__":
    async def main():
        dashboard = AgentHealthCard()
        await dashboard.display_health_dashboard()

    asyncio.run(main())