FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

COPY app ./app

ENV PYTHONPATH="/app/app"

EXPOSE 8080
CMD ["uv", "run", "uvicorn", "app.main:app", "--host=0.0.0.0", "--port=8080"]
