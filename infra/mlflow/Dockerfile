FROM python:3.12.13-slim

ARG MLFLOW_PORT

ENV MLFLOW_PORT=$MLFLOW_PORT
# Python console output optimizations
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/mlflow
# Optimize uv engine for lightweight layer copying
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /mlflow

COPY --from=ghcr.io/astral-sh/uv:0.11.10 /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --only-group mlflow --no-install-project

# Expose uv's virtual environment binaries directly to the terminal environment
ENV PATH="/mlflow/.venv/bin:$PATH"
