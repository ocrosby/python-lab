# FastAPI Project

A production-ready FastAPI application.

## Requirements

- Docker and Docker Compose

## Running the Application

Start the production server:

```bash
docker compose up --build
```

The API will be available at `http://localhost:8080`

## API Documentation

- Swagger UI: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc`

## Development

Install dependencies locally:

```bash
uv sync
```

Run the development server:

```bash
uv run uvicorn main:app --reload
```
