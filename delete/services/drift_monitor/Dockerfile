FROM python:3.12.13-slim

ARG DRIFT_MONITOR_PORT

ENV DRIFT_MONITOR_PORT=$DRIFT_MONITOR_PORT
# Python console output optimizations
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app
# Optimize uv engine for lightweight layer copying
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.11.10 /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --only-group drift_monitor --no-install-project

COPY /services/drift_monitor ./services/drift_monitor
COPY /services/shared ./services/shared

# Expose uv's virtual environment binaries directly to the terminal environment
ENV PATH="/app/.venv/bin:$PATH"

CMD exec uvicorn services.drift_monitor.src.main:app --host 0.0.0.0 --port $DRIFT_MONITOR_PORT --workers 1
