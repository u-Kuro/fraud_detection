FROM python:3.12.13-slim AS builder

WORKDIR /app

ENV UV_LINK_MODE=copy
ENV UV_COMPILE_BYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PATH="/app/.venv/bin:$PATH"

COPY --from=ghcr.io/astral-sh/uv:0.11.10 /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --only-group drift_check --no-install-project

COPY services/__init__.py ./services/__init__.py

FROM builder AS test

RUN uv sync --frozen --only-group drift_check --only-group test --no-install-project

COPY services/drift_check ./services/drift_check
COPY services/shared ./services/shared

RUN python -m pytest services/drift_check/tests/unit/ services/shared/tests/unit/ --quiet

FROM builder AS runtime

COPY services/drift_check/src ./services/drift_check/src
COPY services/shared/src ./services/shared/src

COPY services/drift_check/__init__.py ./services/drift_check/__init__.py
COPY services/shared/__init__.py ./services/shared/__init__.py

RUN useradd --create-home app_user && chown --recursive app_user /app
USER app_user

CMD ["python", "-m", "services.drift_check.src.main"]