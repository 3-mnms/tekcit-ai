FROM python:3.12-slim AS base

# 환경 변수 설정 (Poetry + Python 최적화)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

FROM base AS build
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root --no-interaction --no-ansi

FROM base AS runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=build /app /app

# 소스 복사 
COPY . .
EXPOSE 8084
CMD ["uvicorn", "review_ai.server.main:app", "--host", "0.0.0.0", "--port", "8084"]