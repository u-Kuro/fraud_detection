FROM python:3.12.13-slim AS builder

WORKDIR /app

ENV UV_LINK_MODE=copy
ENV UV_COMPILE_BYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PATH="/app/.venv/bin:$PATH"

COPY --from=ghcr.io/astral-sh/uv:0.11.10 /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --only-group train_model --no-install-project

COPY services/__init__.py ./services/__init__.py

FROM builder AS test

RUN uv sync --frozen --only-group train_model --only-group test --no-install-project

COPY services/train_model ./services/train_model
COPY services/shared ./services/shared

RUN python -m pytest services/train_model/tests/unit/ services/shared/tests/unit/ --quiet

FROM builder AS runtime

COPY services/train_model/src ./services/train_model/src
COPY services/shared/src ./services/shared/src

COPY services/train_model/__init__.py ./services/train_model/__init__.py
COPY services/shared/__init__.py ./services/shared/__init__.py

RUN useradd --create-home app_user && chown --recursive app_user /app
USER app_user

CMD ["python", "-m", "services.train_model.src.main"]