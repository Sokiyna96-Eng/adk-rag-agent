FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

COPY app ./app

EXPOSE 8501
CMD ["uv", "run", "streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
