FROM python:3.12.13-slim

ARG FRAUD_API_PORT

ENV FRAUD_API_PORT=$FRAUD_API_PORT
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

RUN uv sync --frozen --only-group fraud_api --no-install-project

COPY /services/fraud_api ./services/fraud_api
COPY /shared ./services/shared

# Expose uv's virtual environment binaries directly to the terminal environment
ENV PATH="/app/.venv/bin:$PATH"

CMD exec uvicorn services.fraud_api.src.main:app --host 0.0.0.0 --port $FRAUD_API_PORT --workers 1
