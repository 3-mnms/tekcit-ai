FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install poetry

ENV POETRY_VIRTUALENVS_IN_PROJECT=true \
    PATH="/app/.venv/bin:$PATH"

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root && poetry show | grep uvicorn

COPY . .

EXPOSE 8084

CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8084"]