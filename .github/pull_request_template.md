# PR Title
> [scope]: short description (e.g., feat(engine): add finnhub adapter)

## Summary
Explain the change in 2–3 sentences. Link the **card ID** and **design_contract**.

- Card: P?.?.?  
- Design contract file: `<path>`

## Rubric Checklist (must be ✅ to merge)
- [ ] **Design contract adherence**
  - [ ] File paths exist & match
  - [ ] Interfaces & signatures match
  - [ ] Constraints honored (e.g., aiohttp, bounded queues, Decimal money)
- [ ] **Tests**
  - [ ] Unit + at least one integration test
  - [ ] Coverage: lines ≥ **85%**, branches ≥ **80%** (attach summary)
- [ ] **Concurrency & Performance**
  - [ ] No sync I/O in event loop
  - [ ] Bounded queues (`maxsize`) & TaskGroup cancellation
- [ ] **Security**
  - [ ] Inputs validated; secrets not logged or hardcoded
  - [ ] Bandit: no HIGH findings; parameterized DB access
- [ ] **Observability**
  - [ ] Structured JSON logs w/ `trace_id` (+ `order_id` where relevant)
- [ ] **Docs & Self‑critique**
  - [ ] README/Docs updated if public surface changed
  - [ ] Self‑critique: ≥ 3 realistic failure modes + rollback plan
- [ ] **Type safety**
  - [ ] `mypy --strict` clean for changed modules

## Self‑Critique (be brutally honest)
1.
2.
3.

## Local Test Instructions
```bash
make dev up     # or docker compose up
pytest -q --maxfail=1 --disable-warnings
```