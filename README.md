## 🤖 Trading Bot with Agent Heartbeat System

A modular, async trading engine with intelligent agents and comprehensive health monitoring.

**Key Features:**
* **Engine** – Python `asyncio`, Supabase, IBKR
* **Agents** – Pluggable trading strategies (SMA, RSI, etc.)
* **Heartbeat System** – Real-time agent health monitoring with dashboard
* **Dashboard** – Live agent status with green/yellow/red indicators

### 🏥 Agent Heartbeat System

The heartbeat system provides real-time monitoring of agent health and performance:

- **Automatic Heartbeats**: Each agent calls `heartbeat()` every execution snapshot
- **Exception Handling**: SMAAgent catches exceptions and stores error details
- **Health Dashboard**: Visual indicators (🟢/🟡/🔴) show agent status
- **Supabase Storage**: All heartbeat data stored in `trading_agent_heartbeats` table

### 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Supabase (optional):**
   ```bash
   cp .env.example .env
   # Edit .env with your Supabase credentials
   ```

3. **Run the heartbeat demo:**
   ```bash
   python demo_heartbeat.py
   ```

4. **View agent health dashboard:**
   ```bash
   python dashboard/agent_health_card.py
   ```

### 📊 Available Demos

- `python demo_heartbeat.py full` - Complete heartbeat system demo
- `python demo_heartbeat.py dashboard` - Health dashboard only  
- `python demo_heartbeat.py sma` - SMA agent with heartbeat

### 🧪 Testing

Run the comprehensive test suite:
```bash
python -m pytest tests/test_heartbeat.py -v
```

### ✅ Acceptance Testing

Validate the key acceptance criteria:

```bash
# Quick test (30 seconds)
python3 test_acceptance.py

# Full acceptance test (5 minutes)
python3 acceptance_test_simple.py
```

**Acceptance Criteria:**
1. 🔴 Killing SMAAgent loop turns card red within 2 minutes
2. 📊 Health table updating in Supabase database

### 🏗️ Project Structure

```
├── infra/supabase/           # Database schema
├── trading_bot/              # Core engine
│   ├── agents/              # Trading agents
│   ├── execution.py         # Heartbeat system
│   └── base_agent.py        # Agent interface
├── dashboard/               # Health monitoring
├── tests/                   # Test suite
└── demo_heartbeat.py        # Live demonstration
``` 