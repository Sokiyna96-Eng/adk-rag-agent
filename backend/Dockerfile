FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

COPY app ./app

ENV PYTHONPATH="/app/app"  

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "main:app", "--host=0.0.0.0", "--port=8000"]
