FROM python:3.12.11-slim

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

RUN uv sync --frozen --only-group train_model --no-install-project

COPY /services/train_model ./services/train_model
COPY /services/shared ./services/shared

# Expose uv's virtual environment binaries directly to the terminal environment
ENV PATH="/app/.venv/bin:$PATH"

CMD ["python", "-m", "services.train_model.src.main"]
