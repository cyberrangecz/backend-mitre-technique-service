FROM python:3.12-slim AS builder
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir uv

RUN uv venv
COPY README.md pyproject.toml uv.lock ./
RUN uv sync

FROM python:3.12-slim AS app
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PATH="/app/.venv/bin:$PATH"
ENV LISTEN_PORT=8001
ENV GUNICORN_WORKER_TIMEOUT=60

COPY crczp crczp
COPY config.yml manage.py ./
COPY --from=builder /app/.venv ./.venv

EXPOSE 8001
ENTRYPOINT ["/app/bin/run-mitre-technique-service.sh"]
