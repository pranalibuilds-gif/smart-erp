# SmartERP Backend

Modern web-based Enterprise Resource Planning (ERP) platform backend.

## Tech Stack
- **FastAPI**: API Framework
- **SQLAlchemy (Async)**: ORM
- **PostgreSQL**: Database
- **Alembic**: Migrations
- **UV**: Package Management

## Setup

### Prerequisites
- Python 3.12+
- [uv](https://github.com/astral-sh/uv)
- PostgreSQL

### Installation
1. Clone the repository
2. Navigate to `backend`
3. Run `uv sync` to install dependencies

### Running the Application
```bash
uv run uvicorn app.main:app --reload
```

### Migrations
```bash
# Generate a migration
uv run alembic revision --autogenerate -m "description"

# Run migrations
uv run alembic upgrade head
```

### Testing
```bash
uv run pytest
```
