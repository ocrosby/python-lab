# Build stage
FROM python:3.13-slim AS builder

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir uv && \
    uv pip install --system --no-cache .

# Runtime stage
FROM python:3.13-slim

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .

EXPOSE 8000

CMD ["uvicorn", "fastapi_oauth_example.app:app", "--host", "0.0.0.0", "--port", "8000"]
