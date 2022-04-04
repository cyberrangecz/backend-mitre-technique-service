FROM python:3.8-slim AS builder

ARG KYPO_PYPI_DOWNLOAD_URL="https://localhost.lan/repository"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIPENV_VENV_IN_PROJECT="enabled"
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app

RUN pip3 install pipenv

COPY Pipfile Pipfile.lock ./
RUN pipenv sync
RUN pipenv run pip3 install gunicorn

FROM python:3.8-alpine AS app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PATH="/app/.venv/bin:$PATH"
ENV LISTEN_IP=0.0.0.0
ENV LISTEN_PORT=8001
ENV GUNICORN_WORKER_TIMEOUT=60

WORKDIR /app
COPY kypo kypo
COPY config.yml manage.py ./
COPY --from=builder /app/.venv /app/.venv

EXPOSE $LISTEN_PORT
CMD gunicorn kypo.mitre_technique_project.wsgi:application --bind $LISTEN_IP:$LISTEN_PORT --timeout $GUNICORN_WORKER_TIMEOUT
