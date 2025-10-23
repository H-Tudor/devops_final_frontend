FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

RUN addgroup --system app
RUN adduser --ingroup app app_user

WORKDIR /app

RUN chown -R app_user:app /app
USER app_user

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Add only what's needed
COPY README.md ./README.md
COPY src ./src

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=.python-version,target=.python-version \
    uv sync --locked --no-dev --no-cache

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["devops-final-frontend", "--server.address=0.0.0.0"]
