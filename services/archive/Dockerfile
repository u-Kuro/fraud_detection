FROM python:3.12.11-slim AS builder

# Optimize uv engine for lightweight layer copying
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.11.10 /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --only-group archive --no-install-project

FROM builder AS test

# Add the test dependency group on top of the production venv
RUN uv sync --frozen --only-group archive --only-group test --no-install-project

# Python path required for local imports and same-named test file discovery
ENV PYTHONPATH=/app
ENV PATH="/app/.venv/bin:$PATH"

COPY /services/archive ./services/archive
COPY /services/shared ./services/shared

RUN python -m pytest services/archive/tests/unit/ services/shared/tests/unit/ -q

FROM python:3.12.11-slim AS runtime

# Python console output optimizations
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app
# Expose uv's virtual environment binaries directly to the terminal environment
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

COPY /services/archive/src ./services/archive/src
COPY /services/shared/src ./services/shared/src

CMD ["python", "-m", "services.archive.src.main"]