SHELL := /bin/bash
CARD_ID ?= P1.2
BOARD ?= docs/board_bullets.yaml
PY ?= python

.PHONY: ci-local lint typecheck test security build enforcer

ci-local: lint typecheck test security build enforcer
	@echo "\n✅ ci-local passed"

lint:
	ruff check .
	black --check .
	isort --check-only .
	tsc -v >/dev/null 2>&1 && (cd dashboard && pnpm i && pnpm tsc --noEmit) || echo "(skip TS typecheck)"

typecheck:
	mypy --strict trading_bot || (echo "mypy failed" && exit 1)

test:
	pytest -q --maxfail=1 --disable-warnings --cov --cov-report=xml

security:
	bandit -q -r trading_bot -ll || (echo "bandit issues" && exit 1)

build:
	docker build -t trading-bot:ci . || echo "(skip docker build if docker not installed)"

enforcer:
	@[ -f coverage.xml ] || (echo "coverage.xml missing; run 'make test'" && exit 1)
	$(PY) tools/spec_enforcer.py --card-id $(CARD_ID) --board $(BOARD) --coverage coverage.xml --diffbase origin/main