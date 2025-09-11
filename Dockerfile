FROM python:3.12-slim

# system dependencies
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# create working dir
WORKDIR /app

# copy poetry config and project files
COPY pyproject.toml poetry.lock* ./

# install poetry
RUN pip install --upgrade pip && pip install poetry

# install dependencies (no virtualenvs)
RUN poetry config virtualenvs.create false && poetry install --no-root

# copy the rest of the code
COPY . .

# expose port
EXPOSE 8003

# run the server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8084"]