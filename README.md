# LabForge API

[![codecov](https://codecov.io/gh/DevOps-With-Brian/labforge-api/graph/badge.svg?token=IzNNegInXX)](https://codecov.io/gh/DevOps-With-Brian/labforge-api)

A FastAPI backend for self-paced courses, enrollments, and attached lab exercises (think “DevOps With Brian” catalog/Udemy-style).

## Requirements

- Python 3.11+
- Poetry
- Docker (optional, for Postgres)

## Project Structure

```
labforge-api/
├── app/
│   ├── __init__.py
│   ├── main.py            # FastAPI application wiring
│   ├── api/               # Routers (courses, enrollments, labs)
│   ├── schemas/           # Pydantic models (course/lab/enrollment)
│   ├── db/                # SQLAlchemy models + async session helpers
│   └── core/config.py     # Settings (DATABASE_URL, etc.)
├── tests/
│   └── test_*             # API tests (courses + health)
├── alembic/               # Migration env and versions
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

## Setup

### Local Development (SQLite default)

1. Install Poetry if you haven't already:

   ```bash
   pip install poetry
   ```

2. Install dependencies:

   ```bash
   poetry install
   ```

3. Run the development server (uses SQLite `labforge.db` by default):

   ```bash
   poetry run uvicorn app.main:app --reload
   ```

4. Open http://localhost:8000/docs to view the API docs.

> Tip: You can create a `.env` file to set `DATABASE_URL` (and any future settings) for both the app and Alembic. Example:  
> `DATABASE_URL=postgresql+asyncpg://labforge:labforge@localhost:5432/labforge`

### Running with Postgres (Docker Compose)

1. Start Postgres and apply migrations:

   ```bash
   docker compose up -d db
   DATABASE_URL=postgresql+asyncpg://labforge:labforge@localhost:5432/labforge \
   poetry run alembic upgrade head
   ```

2. Start the API (Compose sets `DATABASE_URL=postgresql+asyncpg://labforge:labforge@db:5432/labforge` inside the container):

   ```bash
   docker compose up api
   ```

3. Combined build/run:

   ```bash
   docker compose up --build
   ```

### Using Docker directly (no Compose)

```bash
docker build -t labforge-api .
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql+asyncpg://labforge:labforge@host.docker.internal:5432/labforge \
  labforge-api
```

## Database & Migrations

- Config: `DATABASE_URL` env var (defaults to `sqlite+aiosqlite:///./labforge.db` for quick dev).
- Apply migrations:

  ```bash
  poetry run alembic upgrade head
  ```

- Downgrade one step:

  ```bash
  poetry run alembic downgrade -1
  ```

Makefile shortcuts: `make db-upgrade`, `make db-downgrade`.

## Testing

Run tests:

```bash
poetry run pytest
```

With coverage:

```bash
poetry run pytest --cov=app --cov-report=term-missing
```

## Linting & Formatting

```bash
poetry run ruff check .
poetry run ruff format .
```

## Key Endpoints

- **Health:** `GET /health`
- **Courses:** `GET/POST /courses`, `GET/PATCH /courses/{course_id}`
- **Enrollments:** `POST/GET /courses/{course_id}/enrollments`
- **Labs:** `POST/GET /courses/{course_id}/labs`

OpenAPI docs: http://localhost:8000/docs or `/redoc`.
