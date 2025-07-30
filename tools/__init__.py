"""
Tools package for trading bot.
Provides alerting and heartbeat monitoring functionality.
"""

from .alert import (
    send_slack,
    send_email,
    send_alert,
    notify_fill,
    notify_heartbeat_missed,
    format_fill_summary,
    format_heartbeat_missed,
    AlertConfig,
    config
)

from .heartbeat import (
    HeartbeatManager,
    heartbeat_manager,
    start_heartbeat_monitoring,
    stop_heartbeat_monitoring,
    register_heartbeat_source,
    send_heartbeat,
    deregister_heartbeat_source,
    get_heartbeat_status
)

__all__ = [
    # Alert functions
    'send_slack',
    'send_email',
    'send_alert',
    'notify_fill',
    'notify_heartbeat_missed',
    'format_fill_summary',
    'format_heartbeat_missed',
    'AlertConfig',
    'config',
    
    # Heartbeat functions
    'HeartbeatManager',
    'heartbeat_manager',
    'start_heartbeat_monitoring',
    'stop_heartbeat_monitoring',
    'register_heartbeat_source',
    'send_heartbeat',
    'deregister_heartbeat_source',
    'get_heartbeat_status'
]