FROM python:3.12.11-slim AS builder

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.11.10 /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --only-group drift_check --no-install-project

FROM builder AS test

RUN uv sync --frozen --only-group drift_check --only-group test --no-install-project

ENV PYTHONPATH=/app
ENV PATH="/app/.venv/bin:$PATH"

COPY /services/drift_check ./services/drift_check
COPY /services/shared ./services/shared

RUN python -m pytest services/drift_check/tests/unit/ services/shared/tests/unit/ -q

FROM python:3.12.11-slim AS runtime

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

COPY /services/drift_check/src ./services/drift_check/src
COPY /services/shared/src ./services/shared/src

CMD ["python", "-m", "services.drift_check.src.main"]