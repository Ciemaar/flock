# DearIdea Bootstrap Guide

This document contains instructions, configurations, and snippets to bootstrap the `dearidea` project in your correct, fresh repository.
It strictly adheres to modern Python 3.12+ standards, an HTMX+FastAPI backend, an async SMTP server, robust testing, and Redis-backed rate limiting.

---

## 1. Project Initialization & Structure

Run this in the root of your fresh repository:

```bash
mkdir -p src/dearidea/api src/dearidea/core src/dearidea/services src/dearidea/templates tests docs .github/workflows
touch src/dearidea/__init__.py
touch src/dearidea/main.py
touch tests/__init__.py
touch tests/conftest.py
touch pyproject.toml
touch .pre-commit-config.yaml
touch docker-compose.yml
touch README.md
touch USER_GUIDE.md
touch DEVELOPER_GUIDE.md
```

## 2. Dependencies & Build Configuration (`pyproject.toml`)

Create `pyproject.toml` at the root. This is your single source of truth.

```toml
[build-system]
requires = ["setuptools>=61.0.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "dearidea"
version = "0.1.0"
description = "Email server and website to correspond with ideas"
readme = "README.md"
requires-python = ">=3.12"
license = { text = "MIT" }
authors = [{ name = "DearIdea Contributors" }]
dependencies = [
    "fastapi>=0.110.0",
    "uvicorn[standard]>=0.29.0",
    "click>=8.1.7",
    "pydantic>=2.7.0",
    "pydantic-settings>=2.2.1",
    "SQLAlchemy[asyncio]>=2.0.29",
    "asyncpg>=0.29.0",
    "redis>=5.0.3",
    "jinja2>=3.1.3",
    "aiosmtpd>=1.4.6",
    "alembic>=1.13.1",
    "python-multipart>=0.0.9",
    "itsdangerous>=2.2.0"
]

[project.optional-dependencies]
dev = [
    "pytest>=8.1.1",
    "pytest-asyncio>=0.23.6",
    "pytest-cov>=5.0.0",
    "hypothesis>=6.100.0",
    "httpx>=0.27.0",
    "ruff>=0.3.5",
    "mypy>=1.9.0",
    "mdformat>=0.7.17",
    "pre-commit>=3.7.0"
]

[project.scripts]
dearidea = "dearidea.main:cli"

[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages.find]
where = ["src"]
namespaces = false

[tool.ruff]
line-length = 80
target-version = "py312"

[tool.ruff.lint]
select = [
    "E", "F", "W", "I", "N", "D", "UP", "YTT", "ANN", "S", "BLE",
    "FBT", "B", "A", "COM", "C4", "DTZ", "T10", "EM", "EXE", "ISC",
    "ICN", "G", "INP", "PIE", "T20", "PYI", "PT", "Q", "RSE", "RET",
    "SLF", "SIM", "TID", "TCH", "INT", "ARG", "PTH", "ERA", "PD",
    "PGH", "PL", "TRY", "NPY", "RUF"
]
ignore = ["ANN101", "ANN102", "D100", "D104", "D203", "D212"]

[tool.ruff.lint.pydocstyle]
convention = "google"

[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_configs = true

[tool.pytest.ini_options]
minversion = "8.0"
addopts = "--cov=src/dearidea --cov-report=term-missing --cov-fail-under=100 -v"
testpaths = ["tests"]
asyncio_mode = "auto"
```

## 3. Local Development Infrastructure (`docker-compose.yml`)

Provide ephemeral Redis and PostgreSQL for development and testing.

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: devuser
      POSTGRES_PASSWORD: devpassword
      POSTGRES_DB: devdb
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

## 4. Code Quality & Formatting (`.pre-commit-config.yaml`)

Run formatters, linters, and type-checkers on commit.

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.5
    hooks:
      - id: ruff
        args: [ --fix ]
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.9.0
    hooks:
      - id: mypy
        additional_dependencies: [ types-redis, types-PyYAML ]
  - repo: https://github.com/executablebooks/mdformat
    rev: 0.7.17
    hooks:
      - id: mdformat
        args: [ --wrap, "80" ]
```

## 5. CI Pipeline (`.github/workflows/ci.yml`)

Automate testing against real (but ephemeral) PostgreSQL and Redis instances.

```yaml
name: CI

on:
  push:
    branches: ["main"]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.12"]

    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: testuser
          POSTGRES_PASSWORD: testpassword
          POSTGRES_DB: testdb
        ports:
          - 5432:5432
        options: --health-cmd pg_isready --health-interval 10s --health-timeout 5s --health-retries 5

      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
        options: --health-cmd "redis-cli ping" --health-interval 10s --health-timeout 5s --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: "pip"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e .[dev]

      - name: Run Ruff Linter and Formatter
        run: |
          ruff check src tests
          ruff format --check src tests

      - name: Run Mypy Type Checker
        run: |
          mypy src tests

      - name: Run mdformat Check
        run: |
          mdformat --check *.md

      - name: Run Pytest
        env:
          DEARIDEA_DATABASE_URL: postgresql+asyncpg://testuser:testpassword@localhost:5432/testdb
          DEARIDEA_REDIS_URL: redis://localhost:6379/0
        run: |
          pytest
```

## 6. Understanding Redis (For `DEVELOPER_GUIDE.md`)

Because Redis is critical to the rate limiting functionality, include this section in your `DEVELOPER_GUIDE.md`:

### What is Redis?
Redis is an in-memory data store. Think of it like a very fast, temporary dictionary that your whole application can access. It doesn't permanently save data to disk (like PostgreSQL), making it perfect for volatile, high-speed operations like caching or counting events over time.

### How DearIdea Uses Redis
We use Redis specifically for **Rate Limiting**. We need to know exactly how many times an IP or user has hit our API or SMTP server within a window of time.

For example, when an email hits `new@dearidea.net`:
1. We check Redis for a key like `rate_limit:unauthenticated:ip:192.168.1.5`.
2. Redis tells us the count is `2`.
3. If the limit is `5`, we allow the request and tell Redis to increment the count (now `3`).
4. If the count is `5`, we reject the request.

Redis automatically deletes these keys after a set time (e.g., 1 hour), naturally resetting the rate limit. You interact with Redis in Python via the `redis.asyncio` client.

## Next Steps for Development

1. **Install tools:** `pip install -e .[dev]`
2. **Install pre-commit hooks:** `pre-commit install`
3. **Start local servers:** `docker compose up -d`
4. **Implement CLI:** Build `src/dearidea/main.py` using `click` to expose `serve-web` and `serve-smtp`.
5. **Implement Settings:** Create `src/dearidea/core/config.py` using `pydantic-settings` to define the rate limits (Unauthenticated, New User, Established User).
