FROM python:3.11-slim

WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy project metadata (changes less frequently)
COPY pyproject.toml poetry.lock* README.md ./

# Configure poetry to not create a virtual environment
RUN poetry config virtualenvs.create false

# Install dependencies (cached unless metadata changes)
RUN poetry install --no-interaction --no-ansi --only main

# Copy source code (changes more frequently)
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
