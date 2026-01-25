# Plural

## Getting Started

```bash
# Start the application
docker compose up --build

# Run database migrations
docker compose exec web alembic upgrade head

# Seed sample data
docker compose exec web python seed.py
```

The API will be available at `http://localhost:8000`

## Running Tests

```bash
docker compose exec web pytest tests/ -v
```

## Database Migrations

```bash
# Apply all migrations
docker compose exec web alembic upgrade head

# Create a new migration
docker compose exec web alembic revision --autogenerate -m "description"

# Rollback one migration
docker compose exec web alembic downgrade -1
```

## Documentation

- **Swagger UI**: http://localhost:8000/docs
- **Admin Panel**: http://localhost:8000/admin
