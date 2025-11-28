FROM python:3.11-slim

WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy poetry files
# Copy project metadata, README (needed for poetry build), and source
COPY pyproject.toml poetry.lock* README.md ./
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./

# Configure poetry to not create a virtual environment
RUN poetry config virtualenvs.create false

# Install dependencies (including installing the current project)
RUN poetry install --no-interaction --no-ansi --only main

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
