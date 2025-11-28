# Tests

This directory contains all tests for the LabForge API.

## Structure

```
tests/
├── unit/              # Unit tests - fast, isolated, mocked dependencies
│   ├── test_course_validation.py
│   └── test_enrollment_schemas.py
├── integration/       # Integration tests - slower, use real database
│   ├── test_courses.py
│   └── test_health.py
└── conftest.py        # Shared fixtures and configuration
```

## Test Types

### Unit Tests (`tests/unit/`)

**Purpose:** Test individual functions, classes, and methods in isolation.

**Characteristics:**

- ✅ Very fast (milliseconds)
- ✅ No external dependencies (database, APIs, file system)
- ✅ Mock all external calls
- ✅ Test business logic and validation
- ✅ Run frequently during development

**Example:**

```python
def test_course_title_max_length():
    """Test that title cannot exceed max length."""
    course_data = {"title": "x" * 141, ...}
    with pytest.raises(ValidationError):
        CourseCreate(**course_data)
```

**When to use:**

- Testing Pydantic schema validation
- Testing utility functions
- Testing business logic calculations
- Testing data transformations

### Integration Tests (`tests/integration/`)

**Purpose:** Test how components work together with real dependencies.

**Characteristics:**

- ⚠️ Slower (seconds)
- ⚠️ Uses real database
- ✅ Tests full request/response flow
- ✅ Tests database queries
- ✅ Tests API endpoints end-to-end
- ✅ Run before commits/deployments

**Example:**

```python
def test_create_and_list_courses():
    """Test creating a course and listing it."""
    response = client.post("/courses", json={...})
    assert response.status_code == 201

    courses = client.get("/courses").json()
    assert len(courses) == 1
```

**When to use:**

- Testing API endpoints
- Testing database interactions
- Testing the full application flow
- Testing authentication/authorization

## Running Tests

```bash
# Run all tests
make test

# Run only unit tests (fast)
make test-unit

# Run only integration tests (slower)
make test-integration

# Run with coverage
make test-cov
make test-cov-unit
make test-cov-integration

# Run specific test file
poetry run pytest tests/unit/test_course_validation.py

# Run specific test
poetry run pytest tests/unit/test_course_validation.py::test_course_create_with_valid_data

# Run with verbose output
poetry run pytest -v

# Run and stop on first failure
poetry run pytest -x
```

## Writing New Tests

### Unit Test Checklist

- [ ] Test one function/method at a time
- [ ] Mock all external dependencies
- [ ] Test edge cases and error conditions
- [ ] Test validation logic
- [ ] Keep tests fast (< 100ms each)

### Integration Test Checklist

- [ ] Test complete user workflows
- [ ] Use real database (automatically cleaned between tests)
- [ ] Test API endpoints end-to-end
- [ ] Test database constraints
- [ ] Verify response formats

## Best Practices

1. **Name tests descriptively**: `test_course_title_cannot_exceed_max_length`
2. **One assertion per test** (when possible)
3. **Use fixtures** for common setup (in `conftest.py`)
4. **Keep unit tests fast**: Mock everything external
5. **Integration tests should be idempotent**: Each test cleans up after itself
6. **Test the happy path AND error cases**

## Database in Tests

Integration tests use a real PostgreSQL database with:

- Automatic table cleanup between tests (via `reset_db` fixture)
- `NullPool` connection pooling to prevent connection reuse issues
- Fresh connections for each test

The database is configured in `tests/conftest.py`.

## CI/CD

All tests run automatically on:

- Pull requests
- Pushes to main branch

See `.github/workflows/ci.yml` for the CI configuration.
