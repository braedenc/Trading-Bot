# CLAUDE.md — Trading‑Bot (Adapted Rules)

> Based on Sabrina Ramonov's "Ultimate AI Coding Guide for Developers (Claude Code)" and video walkthrough; tailored to our stack (Python asyncio engine + Next.js dashboard + Supabase). Use with Claude Code and Cursor Rules.

## 0 — Purpose

Keep the codebase production‑grade while enabling fast AI‑assisted development. **MUST** rules are CI‑enforced. **SHOULD** rules are strong conventions.

---

## 1 — Before Coding

* **BP‑1 (MUST)** Ask clarifying questions in PR body when acceptance criteria or design\_contract are ambiguous. (PR template enforces a section.)
* **BP‑2 (SHOULD)** Draft an approach for complex work and compare to similar code in this repo.
* **BP‑3 (SHOULD)** If ≥2 approaches exist, list pros/cons and pick the simplest that fits constraints.

---

## 2 — While Coding

### Python (engine, risk, data, api)

* **C‑1 (MUST)** TDD: write a failing `pytest` first (unit or property‑based), then implement.
* **C‑2 (MUST)** Use domain vocabulary: Engine, Agent, RiskGuard, BrokerGateway, Bar.
* **C‑3 (MUST)** **No float money**; use `Decimal` or integer minor units.
* **C‑4 (MUST)** No sync I/O in the event loop; use `aiohttp`/`anyio` only.
* **C‑5 (MUST)** Bounded queues: `asyncio.Queue(maxsize=10_000)` and expose `queue_depth` metric.
* **C‑6 (MUST)** Lifecycle via `asyncio.TaskGroup`; cancel on `Engine.stop()`.
* **C‑7 (SHOULD)** Prefer small, composable, testable functions; avoid premature classes.
* **C‑8 (SHOULD)** Type hints required; `mypy --strict` must pass for touched modules.
* **C‑9 (SHOULD)** Use `typing.NewType` for IDs: `OrderId = NewType("OrderId", str)`.

### TypeScript (dashboard)

* **TS‑1 (MUST)** Use `import type { … }` for type‑only imports; default to `type` over `interface` (unless merging).
* **TS‑2 (MUST)** Validate all API payloads with **Zod** before use.
* **TS‑3 (MUST)** Use branded types for IDs, e.g. `type OrderId = Brand<string, 'OrderId'>`.
* **TS‑4 (SHOULD)** Minimize comments; prefer self‑explanatory code and good names.

---

## 3 — Testing

* **T‑1 (MUST)** Separate **unit** vs **integration** tests. Pure logic in unit tests; DB/network in integration.
* **T‑2 (MUST)** Coverage thresholds: lines ≥ **85%**, branches ≥ **80%** on changed files.
* **T‑3 (MUST)** Risk & strategy logic include **property‑based tests** (Hypothesis).
* **T‑4 (SHOULD)** Prefer integration tests (with local stubs) over heavy mocking.
* **T‑5 (SHOULD)** Test whole‑result equality over piecemeal asserts when clear.

Python example (property test):

```python
from hypothesis import given, strategies as st
from trading_bot.risk.guards import RiskGuard, RiskError

@given(size=st.integers(min_value=1, max_value=1_000), price=st.decimals(min_value='1', max_value='10000', places=2))
def test_risk_never_allows_notional_breach(size, price):
    rg = RiskGuard(max_notional=1_000_000)
    order = make_order(size=size, price=price)  # helper creates a valid OrderCtx
    if size * price > 1_000_000:
        with pytest.raises(RiskError):
            rg.check(order)
```

---

## 4 — Database & Data Access

* **D‑1 (MUST)** ORM: SQLAlchemy 2.0; strictly parameterized queries; no string‑formatted SQL.
* **D‑2 (MUST)** Supabase **RLS** on user‑facing tables; write via service role only as specified.
* **D‑3 (SHOULD)** Define typed repository interfaces (Protocols) for easier testing.

---

## 5 — Code Organization (repo‑specific)

```
trading_bot/
  engine/        # core loop, task orchestration
  data/          # adapters (e.g., finnhub_adapter.py)
  broker/        # gateways (ibkr.py, sim.py)
  risk/          # guards and policies
  api/           # FastAPI/Starlette endpoints
  types.py       # common dataclasses/typing aliases (Money, OrderId, etc.)
  tests/
dashboard/       # Next.js app (App Router)
docs/            # Roadmap_v1.1.md, Agent_Prompt.md, board_bullets.yaml, CLAUDE.md
infra/           # IaC (optional)
```

* **O‑1 (MUST)** Put shared code in `trading_bot/` only if used by ≥2 modules; FE‑shared goes under `dashboard/src/lib`.

---

## 6 — Tooling Gates

* **G‑1 (MUST)** Python: `ruff`, `black --check`, `mypy --strict`, `pytest --cov --cov-report=xml`.
* **G‑2 (MUST)** Frontend (if `dashboard/` present): `prettier --check .`, `eslint . --max-warnings 0`, `tsc --noEmit`.
* **G‑3 (MUST)** Security: `bandit -q -r trading_bot -ll`, Trivy/Checkov if tools available.
* **G‑4 (MUST)** Observability: structured JSON logs include `trace_id` (and `order_id` when relevant).

---

## 7 — Git

* **GH‑1 (MUST)** Conventional Commits. Example: `feat(engine): add TaskGroup shutdown`
* **GH‑2 (MUST NOT)** Mention "Claude" or "Anthropic" in commit messages.

---

## 8 — Shortcuts (for Claude/Cursor)

### QNEW

```
Understand and adopt all best practices in CLAUDE.md. Follow them by default.
```

### QPLAN

```
Analyze similar code in this repo and propose a plan that:
- is consistent with the codebase
- introduces minimal changes
- reuses existing code
```

### QCODE

```
Implement the approved plan. Ensure tests pass. Run:
- make ci-local  # lint, typecheck, tests, security, build, enforcer
```

### QCHECK

```
SKEPTICAL review of major changes using:
1) Writing Functions checklist
2) Writing Tests checklist
3) Implementation Best Practices
```

### QCHECKF / QCHECKT

```
Analyze all major functions/tests added or modified against the respective checklists.
```

### QUX

```
Act as a human UX tester. List prioritized scenarios to test in the dashboard.
```

### QGIT

```
Stage, commit, and push. Commit message must follow Conventional Commits and must not mention Claude/Anthropic.
```

---

## 9 — Enforcement Hooks (how CI checks these)

* PR Template enforces: clarifying questions, self‑critique, Card ID, coverage.
* Spec Enforcer checks: design‑contract file/interface presence; coverage gates; banned sync I/O; bounded queues; observability fields.
* Commit‑message gate (CI job) enforces Conventional Commits and bans "Claude|Anthropic" mentions.
* Frontend job enforces Prettier/ESLint/TS typecheck when `dashboard/` exists.

---

## 10 — Sources

* Sabrina Ramonov, *The ULTIMATE AI Coding Guide for Developers (Claude Code)* (tailor CLAUDE.md to your codebase; includes QNEW/QPLAN/QCODE/QCHECK/QUX/QGIT workflow).
* Video walkthrough (same guide); follow the process for planning → coding → review.