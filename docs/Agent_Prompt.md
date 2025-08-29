# Agent Operating Brief — Trading‑Bot (Updated)

**Repository:** `braedenc/Trading-Bot` — operate **only** on this repo (do **not** create a new one).

**Mission:** Implement the roadmap and design‑contracts to deliver a production‑grade trading engine (Python asyncio), SMA strategy, Next.js dashboard, and a verifiable audit trail.

---

## Start Here (Task Order)

1. **P0.4 — Baseline tag**: create `v0.1-pre-agent` on `origin/main` and open a short PR with verification log.
2. **P1.2 — CI gates + CLAUDE rules**: add board + repo artifacts and make CI green.
3. Proceed phase‑wise per `docs/board_bullets.yaml`.

> Every PR body **must include** a line: `Card: P?.?.?`

---

## Guardrails (must follow)

* **Design‑contracts**: implement exactly as specified in `docs/board_bullets.yaml` (file paths, interfaces, constraints, tests).
* **Quality rubric**: PRs must score **≥ 9/10** (enforced by `tools/spec_enforcer.py`).
* **Concurrency & perf**: no sync I/O in engine; bounded queues; `TaskGroup` with correct cancellation.
* **Security**: validate inputs; no secrets in code/logs; parameterized DB; Bandit/Trivy/Checkov clean.
* **Observability**: structured JSON logs with `trace_id` (and `order_id` where relevant).
* **Compliance**: audit events are HMAC‑signed and stored on S3 with Object‑Lock (COMPLIANCE).
* **Docs**: update docs when changing public surfaces; include a self‑critique (≥3 realistic failure modes).

---

## References (read these before coding)

* `docs/Roadmap_v1.1.md` — full roadmap + CI/CD Green Playbook + global design‑contract addenda.
* `docs/board_bullets.yaml` — the **design\_contract** source of truth for each card.
* `docs/CLAUDE.md` — adapted Sabrina Ramonov rules (QNEW/QPLAN/QCODE/QCHECK/QUX/QGIT). **Follow by default.**
* `.github/pull_request_template.md` — PR checklist (clarifying questions, coverage, rubric, etc.).
* `tools/spec_enforcer.py` — scores PRs and blocks < 9/10.
* `.github/workflows/ci.yml` — pipeline with: lint → typecheck → test (coverage.xml) → security → build → **spec‑enforcer** → **commit‑messages** → **frontend** (conditional).
* `Makefile` — `make ci-local` runs the whole stack locally.

---

## PR Rubric (enforced)

* Score **≥ 9/10** via `tools/spec_enforcer.py` reading `docs/board_bullets.yaml` + `coverage.xml`.
* Coverage: **lines ≥ 85%**, **branches ≥ 80%** for changed files.
* Commit messages follow **Conventional Commits** and **must not** mention "Claude"/"Anthropic" (CI gate).

---

## Working the Board

* Pick next **Backlog** item from `docs/board_bullets.yaml`, branch `phaseX-Y_short-title`, implement to **design\_contract**, open PR with `Card: <ID>`, move to **In Review**.
* Do not deviate from the contract without a PR comment and approval.

---

## Shortcuts

* **QNEW**: adopt all rules from `docs/CLAUDE.md`.
* **QPLAN**: propose a plan consistent with repo; minimal changes; reuse existing code.
* **QCODE**: implement plan; run `make ci-local`.
* **QCHECK / QCHECKF / QCHECKT**: skeptical reviews using CLAUDE.md checklists.
* **QUX**: list prioritized UX scenarios for the dashboard.
* **QGIT**: stage, commit, push using Conventional Commits; never mention Claude/Anthropic.

---

## Do Not

* Do **not** create a new repo or sub‑repos.
* Do **not** bypass tests, coverage gates, or the spec enforcer.
* Do **not** commit secrets or disable security scanners.

---

# Appendix — Exact PR Text (Copy‑Paste)

## PR #1 — P0.4 Baseline Tag

**Title:** `chore(repo): baseline tag v0.1-pre-agent`

**Body:**

```
Card: P0.4

Summary: Create baseline tag v0.1-pre-agent on origin/main before agent work begins.

Verification (paste actual output):
```

```
git ls-remote --tags origin 'v0.1-*'
```

Checklist:

* [x] Tag pushed to origin
* [x] Visible under GitHub → Releases/Tags

```

---

## PR #2 — P1.2 CI Bootstrap + CLAUDE Rules
**Title:** `chore(ci): establish rubric gates + CLAUDE rules`

**Body:**
```

Card: P1.2

Summary: Bootstrap CI gates and enforce CLAUDE rules.

* Adds: docs/board\_bullets.yaml, docs/Roadmap\_v1.1.md, docs/Agent\_Prompt.md, docs/CLAUDE.md
* Adds: .github/pull\_request\_template.md, tools/spec\_enforcer.py, Makefile
* CI: lint → typecheck → test (coverage.xml) → security → build → spec-enforcer → commit-messages → frontend (conditional)

Coverage summary (attach from CI):

* Lines: \_\_%
* Branches: \_\_%

Spec Enforcer:

* SCORE=\_\_ / 10 (must be ≥ 9)

Checklist:

* [x] PR template used; includes clarifying questions & self-critique
* [x] coverage.xml emitted and attached in summary
* [x] Conventional Commits; no "Claude/Anthropic" mentions in commit subjects
* [x] Required checks enabled on main (lint,typecheck,test,security,build,spec-enforcer,commit-messages,frontend\*)
  \*frontend is required once dashboard/ exists

```
```