Trading Bot PRD (v 0.5 — 20 Jun 2025)
1 – Overview
Modular, async trading engine with plug-in agents.

Engine: Python asyncio, Supabase (Postgres), IBKR

Data: 1-minute OHLCV bars + configurable tick buffer (default 20)

Agents: Live in trading_bot/agents/, inherit BaseAgent.



Dashboard: Lovable.dev front-end, Supabase back-end.

Auth (Phase 1): single Supabase user, RLS off (will revisit when multi-user needed).

2 – Current Repo Layout
sql
Copy
Edit
Trading-Bot/
├── docs/                 <-- PRD + other design notes

├── trading_bot/          <-- engine + agents
├── infra/supabase/       <-- schema.sql + future migrations
├── requirements.txt
├── README.md   LICENSE   .git*
3 – Goals & KPIs (unchanged)
KPI	Target (MVP)
90-day Sharpe	≥ 1.5
Hit-rate	≥ 55 %
Intraday drawdown	≤ 2 % AUM
Signal → Broker ACK	≤ 600 ms
Engine uptime (RTH)	≥ 99 %

4 – Functional Roadmap
Milestone	Target date	Status
M1 – Clean repo + submodule wrapper	20 Jun 2025	✅
M2 – Hourly risk_limits refresh (Supabase)	24 Jun 2025	⬜
M3 – Lovable.dev dashboard v0.1 (positions + P/L)	01 Jul 2025	⬜
M4 – Paper-trade loop (IBKR demo)	05 Jul 2025	⬜
M5 – First live micro-allocation	12 Jul 2025	⬜

5 – Engine vs. Agent Contract (blueprint)
5.1 Engine responsibilities
Layer	Mandatory features	Future hooks
DataFeed	Async bars + tick cache (TickStore)	Adapter interface → new data vendors
TickStore	InMemoryTickStore (param ticks_per_symbol, default 20)	Swap Redis later
RiskManager	Global + per-agent caps, refreshed hourly from Supabase	Risk-rule API for training sims
BrokerRouter	IBKR async; --dry-run, --paper, --live flags	Add crypto/futures routers
State & Metrics	Global position map; fills / P & L → Supabase	Pub-sub bus for dashboards
Agent Fan-out	asyncio.gather() per snapshot	IPC queue for out-of-process agents

 

5.2 Agent contract (frozen)
python
Copy
Edit
class BaseAgent(ABC):
    async def generate_signals(self, snapshot: dict) -> list[dict]: ...
    async def on_fill(self, fill: dict): ...
    async def on_limit_update(self, limits: dict): ...
Agent never calls broker or DB directly.

5.3 Feature split cheat-sheet
Concern	Engine	Agent
Data ingest / tick cache	✅	❌
Signal / sizing logic	❌	✅
Final risk caps	✅	❌ (read-only)
Order routing / retry	✅	❌
Model training / reload	❌	✅

6 – Non-Functional Reqs (delta)
Security: .env secrets; single-user auth (Supabase RLS OFF in Phase 1).

Tick buffer: Configurable per symbol via TickStore constructor.

Observability: Structured logs → Loki; OTEL traces.

Compliance: Submodule keeps upstream license separate; root is MIT.

7 – Phase 2 placeholder
Meta-agent / portfolio allocator – revisit after Phase 1 KPIs met.

8 – Open Questions
Dashboard auth toggle for Phase 2?

Default ticks_per_symbol—leave at 20 or auto-size by liquidity?

9 – Changelog
Ver	Date	Notes
0.5	20 Jun 2025	Adds tick-buffer configurability, finalizes BaseAgent API, clarifies single-user auth.
0.4	20 Jun 2025	First cleaned repo version (superseded).
