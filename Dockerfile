# syntax=docker/dockerfile:1.7

ARG PYTHON_IMAGE=python:3.12-slim

# ---------- Builder ----------
FROM ${PYTHON_IMAGE} AS builder
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# System deps (kept minimal; manylinux wheels cover numpy/pandas)
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Pre-copy manifests to leverage Docker layer cache
COPY pyproject.toml poetry.lock* requirements.txt* ./

# Create venv and install deps (prefer requirements.txt; fallback to Poetry export; else no-op)
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install -U pip wheel setuptools \
 && if [ -f requirements.txt ]; then \
      pip install -r requirements.txt; \
    elif [ -f pyproject.toml ] && grep -q "\[tool.poetry\]" pyproject.toml; then \
      pip install poetry && poetry export -f requirements.txt --output /tmp/req.txt --without-hashes && pip install -r /tmp/req.txt; \
    else \
      echo "No requirements.txt or Poetry project detected; proceeding"; \
    fi

# Now copy the full source
COPY . .

# Optional: install the package itself if desired
# RUN pip install -e .

# ---------- Runtime ----------
FROM ${PYTHON_IMAGE} AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PATH="/opt/venv/bin:$PATH"
WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app /app

# Healthcheck is a no-op; replace with a real one when API exists
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python -c "import sys; sys.exit(0)"

# Default command is inert for CI images — override in Render/Vercel or docker-compose
CMD ["python", "-c", "print('trading-bot image built')"]