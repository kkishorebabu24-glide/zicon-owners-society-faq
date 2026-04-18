# Society App - Backend

FastAPI backend for the Society App community platform.

## Tech Stack

- Python 3.10+
- FastAPI
- SQLAlchemy (ORM)
- PostgreSQL
- Redis
- Alembic (migrations)

## Quick Start

See [../docs/developer-guide.md](../docs/developer-guide.md) for detailed setup instructions.

```bash
# Setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure
cp .env.example .env

# Database
alembic upgrade head

# Run
uvicorn app.main:app --reload
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application
│   ├── config.py                  # Configuration
│   ├── dependencies.py            # Dependency injection
│   ├── api/
│   │   ├── routes/
│   │   │   ├── auth.py           # Authentication endpoints
│   │   │   ├── digests.py        # Digest endpoints
│   │   │   ├── demand_supply.py  # Marketplace endpoints
│   │   │   └── telegram.py       # Telegram webhook
│   ├── core/
│   │   ├── security.py           # Auth logic
│   │   └── config.py             # Core settings
│   ├── db/
│   │   ├── base.py               # SQLAlchemy setup
│   │   ├── session.py            # Database session
│   │   └── models.py             # Data models
│   ├── schemas/                  # Pydantic validation
│   ├── services/                 # Business logic
│   ├── workers/                  # Background tasks
│   └── utils/
├── tests/                        # Unit & integration tests
├── migrations/                   # Alembic migrations
├── requirements.txt
├── .env.example
├── setup.cfg
├── Dockerfile
└── docker-compose.yml
```

## Environment Variables

See `.env.example` for all available variables.

Key variables:
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `SECRET_KEY`: JWT secret key
- `TELEGRAM_BOT_TOKEN`: Telegram bot token
- `OPENAI_API_KEY`: OpenAI API key

## Testing

```bash
# All tests
pytest

# With coverage
pytest --cov=app

# Specific test
pytest tests/test_auth.py -v
```

## Documentation

- [Architecture](../docs/architecture.md)
- [API Docs (Swagger)](http://localhost:8000/docs)
- [Developer Guide](../docs/developer-guide.md)

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md)
