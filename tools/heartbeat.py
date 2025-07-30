"""
Heartbeat monitoring system for trading bot.
Tracks agent heartbeats and sends alerts when missed.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Set
from dataclasses import dataclass, field

from .alert import notify_heartbeat_missed

logger = logging.getLogger(__name__)


@dataclass
class HeartbeatStatus:
    """Status of a single heartbeat source."""
    name: str
    last_heartbeat: datetime
    is_active: bool = True
    missed_count: int = 0


class HeartbeatManager:
    """
    Manages heartbeat tracking and notifications.
    """
    
    def __init__(self, heartbeat_timeout: int = 10):
        """
        Initialize heartbeat manager.
        
        Args:
            heartbeat_timeout: Timeout in minutes before considering heartbeat missed
        """
        self.heartbeat_timeout = heartbeat_timeout
        self.heartbeats: Dict[str, HeartbeatStatus] = {}
        self.is_running = False
        self.check_interval = 60  # Check every minute
        self._monitor_task: Optional[asyncio.Task] = None
        
    async def register_source(self, name: str) -> None:
        """
        Register a new heartbeat source.
        
        Args:
            name: Name of the heartbeat source
        """
        if name not in self.heartbeats:
            self.heartbeats[name] = HeartbeatStatus(
                name=name,
                last_heartbeat=datetime.now()
            )
            logger.info(f"Registered heartbeat source: {name}")
        
    async def heartbeat(self, name: str) -> None:
        """
        Record a heartbeat from a source.
        
        Args:
            name: Name of the heartbeat source
        """
        current_time = datetime.now()
        
        if name not in self.heartbeats:
            await self.register_source(name)
        
        status = self.heartbeats[name]
        status.last_heartbeat = current_time
        status.is_active = True
        status.missed_count = 0
        
        logger.debug(f"Heartbeat received from {name} at {current_time}")
        
    async def deregister_source(self, name: str) -> None:
        """
        Deregister a heartbeat source.
        
        Args:
            name: Name of the heartbeat source
        """
        if name in self.heartbeats:
            del self.heartbeats[name]
            logger.info(f"Deregistered heartbeat source: {name}")
            
    async def start_monitoring(self) -> None:
        """Start the heartbeat monitoring task."""
        if self.is_running:
            logger.warning("Heartbeat monitoring is already running")
            return
        
        self.is_running = True
        self._monitor_task = asyncio.create_task(self._monitor_heartbeats())
        logger.info("Heartbeat monitoring started")
        
    async def stop_monitoring(self) -> None:
        """Stop the heartbeat monitoring task."""
        if not self.is_running:
            return
        
        self.is_running = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Heartbeat monitoring stopped")
        
    async def _monitor_heartbeats(self) -> None:
        """Main monitoring loop."""
        while self.is_running:
            try:
                await self._check_heartbeats()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in heartbeat monitoring: {e}")
                await asyncio.sleep(self.check_interval)
                
    async def _check_heartbeats(self) -> None:
        """Check all heartbeats for timeouts."""
        current_time = datetime.now()
        timeout_threshold = timedelta(minutes=self.heartbeat_timeout)
        
        for name, status in self.heartbeats.items():
            if not status.is_active:
                continue
                
            time_since_last = current_time - status.last_heartbeat
            
            if time_since_last > timeout_threshold:
                # Heartbeat missed
                status.missed_count += 1
                logger.warning(
                    f"Heartbeat missed for {name}: {time_since_last.total_seconds()/60:.1f} minutes"
                )
                
                # Send notification (only on first miss to avoid spam)
                if status.missed_count == 1:
                    try:
                        await notify_heartbeat_missed(status.last_heartbeat, current_time)
                        logger.info(f"Sent heartbeat missed notification for {name}")
                    except Exception as e:
                        logger.error(f"Failed to send heartbeat notification for {name}: {e}")
                
                # Mark as inactive after notification
                status.is_active = False
                
    def get_status(self) -> Dict[str, Dict]:
        """
        Get current status of all heartbeat sources.
        
        Returns:
            Dict with status information for each source
        """
        current_time = datetime.now()
        status_info = {}
        
        for name, status in self.heartbeats.items():
            time_since_last = current_time - status.last_heartbeat
            status_info[name] = {
                'name': name,
                'last_heartbeat': status.last_heartbeat.isoformat(),
                'is_active': status.is_active,
                'missed_count': status.missed_count,
                'minutes_since_last': time_since_last.total_seconds() / 60,
                'is_overdue': time_since_last.total_seconds() / 60 > self.heartbeat_timeout
            }
            
        return status_info
        
    def get_active_sources(self) -> Set[str]:
        """Get set of active heartbeat sources."""
        return {name for name, status in self.heartbeats.items() if status.is_active}
    
    def get_overdue_sources(self) -> Set[str]:
        """Get set of overdue heartbeat sources."""
        current_time = datetime.now()
        timeout_threshold = timedelta(minutes=self.heartbeat_timeout)
        
        return {
            name for name, status in self.heartbeats.items()
            if (current_time - status.last_heartbeat) > timeout_threshold
        }


# Global heartbeat manager instance
heartbeat_manager = HeartbeatManager()


# Convenience functions
async def start_heartbeat_monitoring(timeout_minutes: int = 10) -> None:
    """Start global heartbeat monitoring."""
    global heartbeat_manager
    heartbeat_manager.heartbeat_timeout = timeout_minutes
    await heartbeat_manager.start_monitoring()


async def stop_heartbeat_monitoring() -> None:
    """Stop global heartbeat monitoring."""
    await heartbeat_manager.stop_monitoring()


async def register_heartbeat_source(name: str) -> None:
    """Register a heartbeat source."""
    await heartbeat_manager.register_source(name)


async def send_heartbeat(name: str) -> None:
    """Send a heartbeat."""
    await heartbeat_manager.heartbeat(name)


async def deregister_heartbeat_source(name: str) -> None:
    """Deregister a heartbeat source."""
    await heartbeat_manager.deregister_source(name)


def get_heartbeat_status() -> Dict[str, Dict]:
    """Get current heartbeat status."""
    return heartbeat_manager.get_status()