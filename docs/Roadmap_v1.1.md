# Trading‑Bot Project Roadmap v1.1 (Full Text)

> **Scope:** Stock & forex trading engine + SMA agent, multi‑user React dashboard, prop‑firm compliance, U.S. jurisdiction only. **Target Effort:** ≈ 600 dev hrs (520 hrs dev + 15 % buffer).

---

## Phase 0 — Governance & Scope  (8 hrs)

|  #    |  Deliverable                    |  Key Tasks                                                                                             |  Acceptance Criteria                                       |
| ----- | ------------------------------- | ------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------- |
|  0.1  |  Vision & Definition‑of‑Done    |  Compile single‑page `docs/vision.md`; set code‑coverage ≥ 85 %, SLOs (LTTD ≤ 15 min, MTTR ≤ 30 min).  |  Vision merged; DoD checklist in repo root.                |
|  0.2  |  Reg‑Scope Memo                 |  Explain asset classes, prop‑firm use, non‑BD status, KYC handled by prop‑firm.                        |  `docs/compliance/scope.md` committed.                     |
|  0.3  |  Prop‑Firm Requirements Matrix  |  Tabulate Topstep, FTMO, Apex, Earn2Trade, Traders Central rules.                                      |  Matrix merged in `/docs/compliance/prop_firm_matrix.md`.  |

---

## Phase 1 — Dev‑Experience Backbone  (30 hrs)

|  Milestone              |  Tasks                                                                                     |  Acceptance Criteria                       |
| ----------------------- | ------------------------------------------------------------------------------------------ | ------------------------------------------ |
|  1.1 Containerised Env  |  Multi‑stage Dockerfile (Python 3.12 + Poetry + vectorbt), `docker‑compose` for FE/BE/db.  |  `docker‑compose run bot pytest` exits 0.  |
|  1.2 GitHub Actions CI  |  Ruff lint → unit tests → coverage → Docker build → deploy preview to Render.              |  PR must be green within 10 min.           |
|  1.3 Secrets Mgmt       |  OIDC → Render/Vercel env vars, no plaintext keys.                                         |  Secret‑scan CI passes.                    |

---

## Phase 2 — Core Engine Skeleton  (45 hrs)

|  Milestone                 |  Tasks                                                                 |  Acceptance Criteria                  |
| -------------------------- | ---------------------------------------------------------------------- | ------------------------------------- |
|  2.1 Async I/O Loop        |  `Engine.start/stop/register_agent`, `asyncio.Queue` tick bus.         |  Bench ≥ 500 k ticks/min on M1.       |
|  2.2 Data Adapters         |  Twelve Data & Finnhub 1‑min bars, retry+jitter, 20‑tick ring buffer.  |  Simulated outage → engine alive.     |
|  2.3 Broker Gateway        |  IBKR via `ib_insync`, paper/live toggle.                              |  E2E order placed/modified/canceled.  |
|  2.4 RiskGuard Middleware  |  Max notional, price‑band ±3×ATR, order‐rate throttle.                 |  Violations trigger circuit‑break.    |

---

## Phase 3 — Plugin API & SMA Agent  (25 hrs)

|  Milestone                |  Tasks                                                                                             |  Acceptance Criteria                |
| ------------------------- | -------------------------------------------------------------------------------------------------- | ----------------------------------- |
|  3.1 Strategy Base Class  |  `on_bar`, `on_tick`, shared order manager.                                                        |  No‑op agent registers and runs.    |
|  3.2 SMA Agent v1         |  Fast/slow windows, long & short, multi‑symbol, position sizing; backtest fixtures with vectorbt.  |  Backtest AAPL‑2024 Sharpe > 0.     |
|  3.3 Heartbeat System     |  `heartbeat()` loop, Supabase `agent_heartbeats` table, dashboard status.                          |  Exception flips status in ≤ 30 s.  |

---

## Phase 4 — Compliance & Audit Trail  (70 hrs)

|  Milestone                         |  Tasks                                                                          |  Acceptance Criteria                    |
| ---------------------------------- | ------------------------------------------------------------------------------- | --------------------------------------- |
|  4.1 Immutable Audit Log           |  Terraform S3 bucket with Object‑Lock **COMPLIANCE** (7‑yr), gzip‑JSON stream.  |  Delete attempt → 403; CI test passes.  |
|  4.2 Lifecycle Reconstruction API  |  FastAPI `/audit/{order_id}` merges engine JSON + IBKR exec.                    |  p95 latency ≤ 5 s.                     |
|  4.3 Deploy & Param Hashing        |  CI writes git SHA, image digest, env‑hash to `supabase.deployments`.           |  Dashboard SHA matches running pod.     |
|  4.4 Clock‑Sync Guard              |  NTP drift check ≤ 50 ms; >50 ms aborts & Slack alert.                          |  Unit drift test passes.                |
|  4.5 Kill‑Switch                   |  Auth‑protected POST `/admin/pause`, halts engine.                              |  Halt latency ≤ 500 ms (p99).           |
|  4.6 Retention & Restore Drill     |  S3 lifecycle → Glacier Deep Archive after 12 mo; quarterly restore script.     |  Sample log restore ≤ 24 h.             |

---

## Phase 5 — React / Next.js Dashboard  (45 hrs)

|  Milestone                |  Tasks                                                             |  Acceptance Criteria             |
| ------------------------- | ------------------------------------------------------------------ | -------------------------------- |
|  5.1 Next.js 14 Scaffold  |  TypeScript, App Router, Tailwind + shadcn/ui, Vercel CI preview.  |  Root route renders.             |
|  5.2 Multi‑User Auth      |  Supabase Auth + NextAuth; roles admin/viewer.                     |  Email signup flow works.        |
|  5.3 Live Widgets         |  Agent status card (SWR), PnL chart (WS), trade blotter.           |  Refresh jitter ≤ 200 ms.        |
|  5.4 Compliance Tab       |  Audit search, engine SHA, kill‑switch toggle (admin only).        |  Permissions enforced.           |
|  5.5 Feature‑Flag Infra   |  LaunchDarkly or Supabase table.                                   |  SMA v2 toggled w/out redeploy.  |

---

## Phase 6 — Observability & SLOs  (20 hrs)

|  Milestone               |  Tasks                                             |  Acceptance Criteria              |
| ------------------------ | -------------------------------------------------- | --------------------------------- |
|  6.1 Structured Logging  |  Loguru JSON → Grafana Loki.                       |  Searchable in <1 min.            |
|  6.2 Metrics             |  Prometheus: orders/min, drawdown, heartbeat lag.  |  Alert if heartbeat gap > 120 s.  |
|  6.3 Incident Playbooks  |  Docs/ops: restart bot, rollback, MTTR drill.      |  Dry‑run meets MTTR goal.         |
|  6.4 DORA Dashboards     |  Grafana board: LTTD, MTTR, change‑fail %.         |  Visible to team.                 |

---

## Phase 7 — Non‑Code Deliverables  (38 hrs)

|  Doc #  |  Deliverable                     |  Contents                                           |  Done‑When                       |
| ------- | -------------------------------- | --------------------------------------------------- | -------------------------------- |
|  7.1    |  Developer Handbook              |  Arch diagram, setup, coding standards.             |  Merged; lint passes.            |
|  7.2    |  Strategy SOPs                   |  Decision tree, risk limits, stop‑loss ladder.      |  Owner approval.                 |
|  7.3    |  Written Supervisory Procedures  |  Roles, escalation, RiskGuard params, kill‑switch.  |  Signed‑off.                     |
|  7.4    |  BCP / DR Plan                   |  RTO 4 h, RPO 30 min, restore steps.                |  Plan tested.                    |
|  7.5    |  Reg 17a‑4 Matrix                |  Record → storage → retention mapping.              |  Peer‑reviewed.                  |
|  7.6    |  Change‑Mgmt SOP                 |  PR template, code‑review rules, SHA logging.       |  Template enforced.              |
|  7.7    |  Prop‑Firm Packet                |  30‑day track‑record CSV, risk metrics.             |  Matches Topstep & FTMO schema.  |
|  7.8    |  Investor Deck                   |  TAM, edge, demo GIFs, roadmap.                     |  PDF ≤ 15 slides.                |
|  7.9    |  User Docs                       |  Onboarding, API tokens, dashboard tour.            |  GitHub Pages published.         |

---

## Phase 8 — Release & Continuous Delivery  (16 hrs)

|  Milestone              |  Tasks                                                   |  Acceptance Criteria                      |
| ----------------------- | -------------------------------------------------------- | ----------------------------------------- |
|  8.1 Blue/Green Deploy  |  Render YAML staging/prod, zero‑downtime switch.         |  Cut‑over < 60 s, no dropped heartbeats.  |
|  8.2 Canary + Alerting  |  5 % traffic 10 min → 100 %; auto‑rollback > 1 % error.  |  Rollback verified in test.               |
|  8.3 KPI Dashboards     |  Grafana: LTTD, MTTR, change‑fail %.                     |  Board live.                              |

---

## Timeline & Effort Summary

*Total dev hrs:* **≈ 600**
*Critical path:* Phase 1 → 2 → 3 → 4 → 5 → 6 → 8.
Overlap Docs (Phase 7) with Phases 4–6.

---

## Key Risks & Mitigations

|  Risk                    |  Likelihood  |  Impact           |  Mitigation                                            |
| ------------------------ | ------------ | ----------------- | ------------------------------------------------------ |
|  Prop‑firm rule changes  |  Med         |  Account reset    |  Sync limits nightly; paramise RiskGuard.              |
|  Object‑Lock mis‑config  |  Low         |  Audit failure    |  Terraform asserts COMPLIANCE mode + quarterly check.  |
|  Kill‑switch misuse      |  Low         |  Unexpected halt  |  Dual‑control RBAC + MFA.                              |
|  IBKR API disconnect     |  Med         |  Trade loss       |  Auto‑restart, circuit‑breaker, paper‑mode tests.      |

---

© 2025 Trading‑Bot Project — v1.1

---

## Agent Boards & Prompt (for GitHub Spark · Claude Code · Gemini Jules · Cursor)

### How to Use

1. These boards map **directly** to the roadmap above.
2. Agents should **self‑assign** tasks, create a branch named `phaseX-Y_short-title`, and open a PR linking to the task line (e.g. `Fixes #P1.1`).
3. **Manual status moves only** (`Backlog → In Progress → Blocked → In Review → Done`).
4. **Acceptance criteria** act as the definition of done; TDD (≥ 85 % coverage) is mandatory.
5. All compliance‑related tasks must reference the *Immutable Audit Log* bucket & S3 Object‑Lock settings.

---

### Milestone‑Level Board (40 cards)

```yaml
- id: P0.1
  phase: 0
  title: Vision & DoD
  effort_hrs: 2
  acceptance: Vision doc merged; DoD checklist committed
- id: P0.2
  phase: 0
  title: Reg-Scope Memo
  effort_hrs: 4
  acceptance: scope.md committed
- id: P0.3
  phase: 0
  title: Prop-Firm Matrix
  effort_hrs: 2
  acceptance: matrix committed
- id: P1.1
  phase: 1
  title: Containerised Env
  effort_hrs: 6
  acceptance: `docker-compose run bot pytest` exits 0
- id: P1.2
  phase: 1
  title: GitHub Actions CI
  effort_hrs: 12
  acceptance: PR green ≤10 min, ruff+tests+coverage≥85 %
- id: P1.3
  phase: 1
  title: Secrets Management
  effort_hrs: 12
  acceptance: no plaintext keys, OIDC works
- id: P2.1
  phase: 2
  title: Async I/O Loop
  effort_hrs: 10
  acceptance: 500k ticks/min benchmark
- id: P2.2
  phase: 2
  title: Data Adapters
  effort_hrs: 10
  acceptance: engine survives feed outage
- id: P2.3
  phase: 2
  title: Broker Gateway (IBKR)
  effort_hrs: 12
  acceptance: paper E2E order life‑cycle
- id: P2.4
  phase: 2
  title: RiskGuard Middleware
  effort_hrs: 13
  acceptance: circuit‑break on rule breach
# … repeat for all phases up to 8.3 …
```

*(Continue list in same pattern; total 40 items. The detailed enumeration is above for quick copy‑paste.)*

---

### Bullet‑Level Board (nested under each milestone)

Below is an **example** for Phase 1.1; replicate pattern for the rest.

```yaml
parent_id: P1.1
children:
  - task: "Write multi‑stage Dockerfile (Python 3.12, Poetry, vectorbt)"
    effort_hrs: 3
    acceptance: Image builds locally; size < 800 MB
  - task: "Add docker‑compose with services: bot, db, supabase, front‑end"
    effort_hrs: 2
    acceptance: `docker compose up` starts all containers
  - task: "Pytest smoke test inside container"
    effort_hrs: 1
    acceptance: pytest exit 0, coverage plugin runs
```

> **Tip:** Keep bullet tasks ≤ 1 day of work; if bigger, split.

Repeat bullet breakdowns for every milestone (approx. 120 tasks). Agents may further break tasks as needed but **must never skip acceptance criteria**.

---

### Comprehensive Prompt (hand this to background agents)

> **You are a background software‑engineering agent working on the *****Trading‑Bot***** project (links below). Your mission is to deliver production‑ready code that satisfies the roadmap and compliance requirements.**
>
> **Context:**
> • Roadmap & boards (above).
> • Full PRD: `https://github.com/braedenc/Trading-Bot/blob/main/docs/PRD.md`
> • Tech stack: Python 3.12, asyncio engine, vectorbt, IBKR, Supabase, React/Next 14, Tailwind+shadcn, Docker, Render/Vercel.
> • Constraints: ≥ 85 % test coverage, strict TDD, U.S. jurisdiction, prop‑firm compliance, S3 Object‑Lock for audit logs, manual board status moves.
> • RiskGuard: max notional, price‑band ±3×ATR, max 5 orders/sec.
>
> **Workflow:**
>
> 1. Pick a card from *Milestone* or *Bullet* board.
> 2. Create branch `phaseX-Y_short-title`.
> 3. Commit incremental TDD code & tests.
> 4. Open PR referencing the board item (`Fixes #P1.2`).
> 5. Ensure CI passes (`ruff`, `pytest`, `coverage`, Docker build).
> 6. Move card `In Review`.
> 7. After human review & merge, move card `Done`.
>
> **Important:**
> • Every code path that touches order placement must emit an audit‑trail event.
> • All env vars managed via GitHub OIDC → Render/Vercel.
> • Use Feature Flags to dark‑launch risky changes.
> • Compliance tab in dashboard must expose kill‑switch & engine SHA.
>
> **Deliverables per task:**
> – Production code + tests
> – Updated docs if public surface changes
> – Checklist in PR description confirming acceptance criteria.

Agents: start with Phase 1.1; ask clarifying questions in PR comments when unsure.

---

*End of Agent Boards & Prompt Section*

---

## Auto‑Audit of Current Repo (high‑confidence scan)

| Milestone                 | Evidence in repo                                                                                 | Status             |          |
| ------------------------- | ------------------------------------------------------------------------------------------------ | ------------------ | -------- |
| **1.2 GitHub Actions CI** | `.github/workflows/ci.yml` exists **but PRs fail**                                               | **Needs Fix**      | **Done** |
| **3.3 Heartbeat System**  | `AGENT_HEARTBEAT_IMPLEMENTATION.md`, `demo_heartbeat.py`, Supabase table SQL in `infra/supabase` | **Done**           |          |
| **3.2 SMA Agent (v1)**    | `trading_bot/agents/sma_agent.py`, tests in `test_strategy_selection.py`                         | **Done**           |          |
| **5.1 FE Scaffold**       | `dashboard/` Vite React‑TS project (needs Next.js migration)                                     | **Partially Done** |          |
| **1.1 Containerised Env** | **No Dockerfile found**                                                                          | **Todo**           |          |
| All other milestones      | No decisive artifacts yet                                                                        | **Todo/Unknown**   |          |

*(Automated scan via repo HTML scrape; false‑negatives possible)*

---

## Bullet‑Level Design Contracts  (Phase‑by‑Phase)

Below is a condensed YAML excerpt. *Agents must replicate pattern for any task not explicitly listed.*

```yaml
# ========= Phase 1 =========
- id: P1.1.1
  parent_id: P1.1
  title: "Create multi‑stage Dockerfile"
  design_contract:
    file: Dockerfile
    constraints:
      - Stage 1: python:3.12‑slim, install poetry & build deps
      - Stage 2: copy `trading_bot`, `dashboard`, `requirements.txt`
      - Final image size < 800 MB
    tests:
      - GH Action builds image; `docker run bot pytest` exits 0

- id: P1.1.2
  parent_id: P1.1
  title: "docker‑compose services"
  design_contract:
    file: docker-compose.yml
    interface: |
      services:
        bot:
          build: .
        db:
          image: supabase/postgres
        front:
          build: ./dashboard
    tests:
      - `docker compose up -d` then `curl localhost:3000` returns 200.

- id: P1.2.1
  parent_id: P1.2
  title: "CI Lint + Unit"
  design_contract:
    file: .github/workflows/ci.yml
    constraints:
      - Use ruff
      - Fail on coverage < 85 %

# ========= Phase 2 =========
- id: P2.1.1
  parent_id: P2.1
  title: "Engine core class"
  design_contract:
    file: trading_bot/engine/core.py
    interface: |
      class Engine:
          async def start(self): ...
          async def stop(self): ...
          def register_agent(self, agent: "BaseAgent"): ...
    constraints:
      - Use asyncio.Queue for ticks
      - No global state
    tests:
      - Simulate 100 k fake ticks; latency < 2 ms p95

- id: P2.2.1
  parent_id: P2.2
  title: "FinnhubAdapter"
  design_contract:
    file: trading_bot/data/finnhub_adapter.py
    interface: |
      class FinnhubAdapter(BaseDataAdapter):
          async def subscribe(self, symbols: list[str]) -> AsyncIterator[Bar]: ...
    constraints:
      - aiohttp client‑session reuse
      - Handle HTTP 429 with back‑off (0.5 s ×2^n)
    tests:
      - aioresponses mock; branch coverage 95 %

- id: P2.4.1
  parent_id: P2.4
  title: "RiskGuard middleware"
  design_contract:
    file: trading_bot/risk/guards.py
    interface: |
      class RiskGuard:
          def check(self, order: OrderCtx) -> None:  # raises RiskError
    constraints:
      - Max notional set via env var `MAX_NOTIONAL`
      - Price band ±3×ATR (14)
    tests:
      - pytest param cases: pass, notional breach, price band breach

# ========= Phase 3 =========
- id: P3.1.1
  parent_id: P3.1
  title: "Strategy base class"
  design_contract:
    file: trading_bot/strategy/base.py
    interface: |
      class BaseStrategy(ABC):
          @abstractmethod
          async def on_bar(self, bar: Bar): ...
          @abstractmethod
          async def on_tick(self, tick: Tick): ...

- id: P3.2.2
  parent_id: P3.2
  title: "SMA crossover logic"
  design_contract:
    file: trading_bot/strategy/sma.py
    interface: |
      class SMAStrategy(BaseStrategy):
          def __init__(self, fast:int=50, slow:int=200): ...
    constraints:
      - Works multi‑symbol
      - Generates OrderCtx w/ position sizing 1 % equity
    tests:
      - vectorbt backtest vs expected equity curve

# ========= Phase 4 =========
- id: P4.1.1
  parent_id: P4.1
  title: "Terraform S3 bucket with Object‑Lock"
  design_contract:
    file: infra/terraform/s3_audit.tf
    constraints:
      - Object‑lock mode: COMPLIANCE, retention = 7 years
      - Encrypted SSE‑AES256
    tests:
      - `terraform validate`; `aws s3api get-object-lock-configuration` pass

- id: P4.2.1
  parent_id: P4.2
  title: "FastAPI audit endpoint"
  design_contract:
    file: trading_bot/api/audit.py
    interface: |
      @router.get("/audit/{order_id}")
      async def audit(order_id:str): ...
    constraints:
      - Query Supabase + S3 pointer; 5 s SLA

# ========= Phase 5 =========
- id: P5.1.1
  parent_id: P5.1
  title: "Next.js 14 app router scaffold"
  design_contract:
    file: dashboard/next.config.mjs
    constraints:
      - TypeScript, Tailwind, shadcn/ui
      - SSR disabled for static routes

- id: P5.4.1
  parent_id: P5.4
  title: "Compliance tab components"
  design_contract:
    file: dashboard/components/CompliancePanel.tsx
    constraints:
      - Shows engine SHA from `/api/version`
      - Kill‑switch POST `/admin/pause`

# ========= Phase 6 =========
- id: P6.1.1
  parent_id: P6.1
  title: "Loguru JSON → Loki"
  design_contract:
    file: trading_bot/infra/logging.py
    constraints:
      - Structured JSON; include `trace_id`

# ========= Phase 7 =========
- id: P7.3
  title: "Written Supervisory Procedures"
  design_contract:
    file: docs/compliance/WSP.md
    constraints:
      - Covers roles, escalation, kill‑switch auth, RiskGuard params

# ========= Phase 8 =========
- id: P8.1.1
  parent_id: P8.1
  title: "Render blue‑green YAML"
  design_contract:
    file: render.yaml
    constraints:
      - `plan: standard`, zero‑downtime
      - Health check `/healthz`
```

*Extend the pattern for any additional bullet tasks not explicitly listed above.*

---

---

## Addendum: Phase 0 — New Deliverable P0.4

| #   | Deliverable                     | Key Tasks                                      | Acceptance Criteria                                   |
| --- | ------------------------------- | ---------------------------------------------- | ----------------------------------------------------- |
| 0.4 | **Baseline Tag v0.1-pre-agent** | Tag current `origin/main` before agents start. | Tag exists remotely; verification log attached in PR. |

### Milestone-Level Board — Added Card

```yaml
- id: P0.4
  phase: 0
  title: Baseline Tag v0.1-pre-agent
  effort_hrs: 0.25
  acceptance: remote tag exists; verification logged in PR
```

### Bullet-Level Board — P0.4 Design Contract

```yaml
parent_id: P0.4
children:
  - task: "Create baseline tag on origin/main"
    design_contract:
      file: N/A (repository state)
      steps:
        - run: git fetch origin main
        - run: git tag v0.1-pre-agent origin/main
        - run: git push --tags
      verification:
        - run: git ls-remote --tags origin "v0.1-*" | grep v0.1-pre-agent
    acceptance: remote tag exists and is visible in GitHub UI; command log pasted into PR
```

---

## 📌 Global PR Rubric (GPT‑5) & Enforcement

**Goal:** Drive PR quality to a repeatable ≥ 9/10 and keep my confidence ≥ 0.90 on plan, quality, and agent delivery.

```yaml
rubric:
  min_score: 9
  checks:
    - name: Design contract adherence
      weight: 2
      rules:
        - file_paths_must_exist: true
        - interfaces_match_signatures: true  # function/class names & params
        - constraints_honored: true          # e.g., aiohttp, bounded queues
    - name: Tests
      weight: 2
      rules:
        - coverage_lines >= 85
        - coverage_branches >= 80
        - at_least_one_integration_test: true
    - name: Concurrency & Perf
      weight: 1
      rules:
        - no_sync_io_in_event_loop: true
        - asyncio_queue_bounded: true
        - cancellation_scopes_present: true  # TaskGroup
    - name: Security
      weight: 2
      rules:
        - inputs_validated: true
        - no_secrets_in_code_or_logs: true
        - sql_parameterized_or_orm: true
        - bandit_no_high_findings: true
    - name: Observability
      weight: 1
      rules:
        - structured_json_logs_with_trace_id: true
        - audit_events_include_order_id: true
    - name: Docs & Self‑critique
      weight: 1
      rules:
        - pr_has_self_critique >= 3_risks
        - docs_or_readme_updated_if_surface_changed: true
    - name: Type safety
      weight: 1
      rules:
        - mypy_strict_clean_for_changed_pkgs: true
```

**Enforcer:** `tools/spec_enforcer.py` (invoked in CI before merge)

* Reads the **design\_contract** from the board YAML for the targeted card(s).
* Verifies file paths, simple AST signature matches, banned APIs, and parses `coverage.xml`.
* Fails PR if computed score < `rubric.min_score`.

**PR Template:** Refer to the canvas doc **"Repo Artifacts — PR Template & Spec Enforcer"** for the authoritative template. In the repo, this must live at `.github/pull_request_template.md`. The template enforces, at minimum:

* Design‑contract adherence (files, interfaces, constraints)

* Tests with coverage thresholds (lines ≥ 85 %, branches ≥ 80 %) and ≥1 integration test

* Concurrency & performance (no sync I/O; bounded queues; TaskGroup cancellation)

* Security (validated inputs; no secrets in code/logs; Bandit no HIGH; parameterized DB)

* Observability (structured JSON logs include `trace_id` and `order_id` where relevant)

* Docs & self‑critique (≥ 3 realistic failure modes + rollback plan)

* Type safety (`mypy --strict` clean for changed modules)

* ## Checklist auto-inserted requiring:

---

## 🧪 CI/CD Green Playbook (Phase 1.2 reinforced)

**Workflow file:** `.github/workflows/ci.yml`

**Jobs:**

1. **lint** → Ruff (pinned), isort, black check
2. **typecheck** → mypy `--strict` for `trading_bot/engine|risk|api`
3. **test** → pytest with coverage + Hypothesis
4. **security** → Bandit (Python), Trivy (container), CodeQL (code), Checkov (IaC)
5. **build** → Docker multi‑stage build + Cosign sign + SLSA provenance

**Key pins & caches:**

* `python-version: 3.12.4`
* Poetry version locked; `POETRY_CACHE_DIR` cached by hash of `poetry.lock`
* `actions/setup-node@v4` for dashboard with pnpm cache by `pnpm-lock.yaml`

**Acceptance (expanded):**

* All jobs green on PR & `main`
* Coverage gates enforced (fail below threshold)
* CodeQL workflow scheduled weekly
* Cosign signature present on image; provenance uploaded as artifact

---

## ⚙️ Global Design‑Contract Addenda (applies to multiple cards)

### Concurrency & Perf

* **Bounded queues**: all `asyncio.Queue` in engine must set `maxsize` (default 10\_000) and expose metric `queue_depth`.
* **Task orchestration**: use `asyncio.TaskGroup` for lifecycle; ensure cancellation on `Engine.stop()`.
* **No sync I/O** in event loop. Network ops use `aiohttp` or `anyio` façade.

### Money & Precision

* All prices/amounts use `Decimal` (quantize to 1e-4 FX, 1e-2 equities) or integer minor units. Provide `Money` type alias.

### Security

* Inputs validated with Pydantic v2 in API; FE validates with Zod.
* Secrets only via env; forbid printing secrets; `secrets.GITHUB_TOKEN` never echoed.
* DB access via SQLAlchemy 2.0 (no raw f‑strings). Prepared statements only.

### Observability

* OpenTelemetry traces (OTLP exporter) for engine, API, and FE fetches; include `trace_id` in logs.
* Log fields: `timestamp, level, module, trace_id, order_id?, symbol?, event_type`.

### Audit‑Log Hardening

* Every audit event is HMAC‑signed using rotating key (`AUDIT_HMAC_KEY_vN`); verify on read.
* S3 Object‑Lock **COMPLIANCE** mode; server‑side encryption enabled.

---

## 🔐 DB & RLS Contracts (Supabase)

* **Schema migrations** with Alembic; versioned in `migrations/`.
* **RLS** enabled for all user‑facing tables; policies:

  * `agent_heartbeats`: read: role `viewer|admin`; write: engine service role only.
  * `audit_events`: read: admin only; write: engine service role only.
* **Acceptance:** RLS tests in `tests/db/test_rls.py` verifying expected 403s.

---

## 🧰 Simulation & Testing Contracts

* **Simulated Broker (**\`\`**)**

  * Behaviors: latency, partial fills, rejects, cancels, rate limits
  * Used in property tests to validate order‑lifecycle invariants
* **Property‑based tests (Hypothesis)**

  * RiskGuard: random order sizes/prices/ATR → invariant: never passes rule breach
  * SMA: random bar streams → no index errors; position sizing stays within limits

---

## 🖥️ Front‑End Contracts

* **API client**: typed fetcher with Zod validation; exp‑backoff + circuit‑breaker
* **Compliance tab**: displays engine SHA, toggles kill‑switch, search audit events by `order_id`
* **Acceptance:** Lighthouse perf score ≥ 90 on dashboard routes

---

## 🔏 Supply Chain & Infra Contracts

* Docker images signed with **Cosign**; provenance (SLSA level 3) emitted
* IaC scanned by **Checkov**; no high severity
* Container scan by **Trivy**; no critical CVEs

---

## ✅ Confidence Levers & Proof Checklist

To push confidence ≥ 0.90 on plan, quality, and agent delivery, the following must be **demonstrably true** before Phase 3 ends:

1. **CI is green** with all gates (lint, mypy, tests, security, build) — attach first green PR URL.
2. **Spec Enforcer** fails at least one intentionally‑broken PR (prove it catches violations).
3. **Sim Broker** completes an end‑to‑end run with SMA on 3 symbols; invariants hold.
4. **Audit logs** restore drill works: event signed → stored (WORM) → reconstructed by API ≤ 5 s.
5. **RLS tests**: forbidden queries 403 as expected; allowed paths succeed.
6. **Tracing demo**: click from dashboard error to correlated API/engine traces.

*When these 6 checks are attached to issues/PRs, confidence ≥ 0.90 is justified and locked.*