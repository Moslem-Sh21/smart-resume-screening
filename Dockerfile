FROM python:3.13-slim

WORKDIR /app

RUN pip install --no-cache-dir uv==0.12.17

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-project

COPY README.md ./
COPY apps ./apps
COPY src ./src

RUN uv sync --frozen

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/live', timeout=2)" || exit 1

CMD ["uv", "run", "uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
