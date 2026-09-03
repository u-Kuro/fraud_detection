FROM python:3.12.11-slim AS builder

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.11.10 /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --only-group train_model --no-install-project

FROM builder AS test

RUN uv sync --frozen --only-group train_model --only-group test --no-install-project

ENV PYTHONPATH=/app
ENV PATH="/app/.venv/bin:$PATH"

COPY /services/train_model ./services/train_model
COPY /services/shared ./services/shared

RUN python -m pytest services/train_model/tests/unit/ services/shared/tests/unit/ -q

FROM python:3.12.11-slim AS runtime

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

COPY /services/train_model/src ./services/train_model/src
COPY /services/shared/src ./services/shared/src

CMD ["python", "-m", "services.train_model.src.main"]