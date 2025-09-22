# 베이스 이미지로 python:3.12-slim 사용
FROM python:3.12-slim

# 필요한 빌드 도구와 패키지를 설치하고, apt 캐시를 정리하여 레이어 크기 최적화
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리를 /app으로 설정
WORKDIR /app

# pip으로 poetry를 직접 설치하여 PATH 문제 해결
RUN pip install poetry

# 프로젝트의 의존성 파일을 먼저 복사하여 Docker 캐싱 활용
COPY pyproject.toml poetry.lock ./

# 의존성 설치. 이 단계는 pyproject.toml이나 poetry.lock이 변경되지 않는 한 캐시됨
RUN poetry install --no-root

# 프로젝트의 나머지 파일 복사
COPY . .

# 애플리케이션이 사용할 포트 8084 노출
EXPOSE 8084

# 애플리케이션 실행 명령어
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8084"]