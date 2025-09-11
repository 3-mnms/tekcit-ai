# ===== 1. Base Image =====
FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# ===== 2. Build Stage =====
FROM base AS build

# build-essential, Rust, libffi 설치 (Chroma 빌드용)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libffi-dev \
        curl \
        git \
    && rm -rf /var/lib/apt/lists/*

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:$PATH"

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root --no-interaction --no-ansi

# ===== 3. Runtime Stage =====
FROM base AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
        libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=build /app /app

COPY . .

EXPOSE 8084

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8084"]