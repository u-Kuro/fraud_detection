FROM python:3.12.13-slim

ARG API_PORT

ENV API_PORT=$API_PORT
ENV UV_SYSTEM_PYTHON=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.11.10 /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"

COPY /api ./api

CMD exec uvicorn api.main:app --host 0.0.0.0 --port $API_PORT --workers 1