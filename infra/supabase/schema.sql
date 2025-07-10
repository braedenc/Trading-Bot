-- Trading Bot Database Schema
-- Supabase (PostgreSQL) schema

-- Agent heartbeat table for monitoring agent health
CREATE TABLE IF NOT EXISTS trading_agent_heartbeats (
    id BIGSERIAL PRIMARY KEY,
    agent_name VARCHAR(255) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_error TEXT DEFAULT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'healthy', -- 'healthy', 'error', 'warning'
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Add index for efficient querying
    INDEX idx_agent_heartbeats_agent_ts (agent_name, timestamp DESC),
    INDEX idx_agent_heartbeats_status (status),
    INDEX idx_agent_heartbeats_created (created_at DESC)
);

-- Add comment for documentation
COMMENT ON TABLE trading_agent_heartbeats IS 'Tracks agent health status and heartbeats for monitoring dashboard';
COMMENT ON COLUMN trading_agent_heartbeats.agent_name IS 'Name of the trading agent (e.g., SMA_Agent)';
COMMENT ON COLUMN trading_agent_heartbeats.timestamp IS 'When the heartbeat was recorded';
COMMENT ON COLUMN trading_agent_heartbeats.last_error IS 'Last error message if any';
COMMENT ON COLUMN trading_agent_heartbeats.status IS 'Current agent status: healthy, error, warning';
COMMENT ON COLUMN trading_agent_heartbeats.metadata IS 'Additional agent metadata (JSON)';

-- View for latest agent status (useful for dashboard)
CREATE OR REPLACE VIEW agent_health_latest AS
SELECT DISTINCT ON (agent_name) 
    agent_name,
    timestamp,
    last_error,
    status,
    metadata,
    created_at
FROM trading_agent_heartbeats
ORDER BY agent_name, timestamp DESC;

COMMENT ON VIEW agent_health_latest IS 'Latest heartbeat status for each agent';

-- Future tables can be added here as the project grows
-- Example: trading_positions, trading_signals, risk_limits, etc.