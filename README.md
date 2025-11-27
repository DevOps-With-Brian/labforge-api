# LabForge API

[![codecov](https://codecov.io/gh/DevOps-With-Brian/labforge-api/graph/badge.svg?token=IzNNegInXX)](https://codecov.io/gh/DevOps-With-Brian/labforge-api)

A FastAPI backend API for managing labs/training for UI.

## Requirements

- Python 3.11+
- Poetry
- Docker (optional)

## Project Structure

```
labforge-api/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   └── models.py        # Pydantic models
├── tests/
│   ├── __init__.py
│   └── test_health.py   # Health endpoint tests
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

## Setup

### Local Development

1. Install Poetry if you haven't already:

   ```bash
   pip install poetry
   ```

2. Install dependencies:

   ```bash
   poetry install
   ```

3. Run the development server:

   ```bash
   poetry run uvicorn app.main:app --reload
   ```

4. Open http://localhost:8000/docs to view the API documentation.

### Using Docker

1. Build and run with Docker Compose:

   ```bash
   docker compose up --build
   ```

2. Or build and run with Docker directly:

   ```bash
   docker build -t labforge-api .
   docker run -p 8000:8000 labforge-api
   ```

3. Open http://localhost:8000/docs to view the API documentation.

## Testing

Run tests with pytest:

```bash
poetry run pytest
```

Run tests with coverage:

```bash
poetry run pytest --cov=app
```

## Linting

Run linting with ruff:

```bash
poetry run ruff check .
```

Format code with ruff:

```bash
poetry run ruff format .
```

## API Endpoints

### Health Check

- **GET** `/health` - Returns health status of the API

  Response:

  ```json
  {
    "status": "healthy",
    "message": "LabForge API is running"
  }
  ```
