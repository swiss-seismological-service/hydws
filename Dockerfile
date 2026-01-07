FROM python:3.13-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl libpq-dev git\
    && rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man \
    && apt-get clean

# Install build backend requirements
RUN pip install --no-cache-dir --upgrade pip wheel setuptools

COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


FROM python:3.13-slim AS app

WORKDIR /hydws

# Install runtime dependencies first (changes less frequently)
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 curl \
    && rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man \
    && apt-get clean

COPY --from=builder /app/wheels /wheels

RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

# Create non-root user after installations
RUN useradd --create-home python \
    && chown python:python -R /hydws

USER python

COPY --chown=python:python . .

ENV PYTHONUNBUFFERED="true" \
    PYTHONDONTWRITEBYTECODE="true" \
    PYTHONPATH="/hydws" \
    PATH="${PATH}:/home/python/.local/bin" \
    USER="python"

EXPOSE 8000

CMD ["bash", "-c", "alembic upgrade head && gunicorn -k uvicorn.workers.UvicornWorker -c python:config.gunicorn hydws.main:app"]
