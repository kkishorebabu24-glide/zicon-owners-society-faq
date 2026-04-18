# Developer Guide

Complete setup and development instructions for Society App.

## Prerequisites

- **Python**: 3.10 or higher
- **Node.js**: 16.0 or higher
- **PostgreSQL**: 14 or higher
- **Redis**: 7 or higher
- **Docker & Docker Compose**: Latest versions (optional but recommended)
- **Git**: Latest version
- **Code Editor**: VS Code, PyCharm, or similar

## Quick Start (Recommended: Docker)

```bash
# Clone repository
git clone https://github.com/yourusername/society-app.git
cd society-app

# Switch to develop branch
git checkout develop

# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Edit .env files with your configuration
# Important: Add API keys (Telegram, OpenAI, etc.)

# Start all services
docker-compose up -d

# Run migrations
docker-compose exec backend alembic upgrade head

# Seed sample data (optional)
docker-compose exec backend python scripts/seed_db.py

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Redis: localhost:6379
# PostgreSQL: localhost:5432
```

## Local Development Setup

### Backend Setup

#### 1. Clone and Navigate

```bash
git clone https://github.com/yourusername/society-app.git
cd society-app/backend
```

#### 2. Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development tools
```

#### 4. Environment Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
# Key variables to set:
# - DATABASE_URL=postgresql://user:password@localhost:5432/society_db
# - REDIS_URL=redis://localhost:6379/0
# - TELEGRAM_BOT_TOKEN=your_token_here
# - OPENAI_API_KEY=your_key_here
# - SECRET_KEY=generate_a_random_secret_key
# - ENVIRONMENT=development
```

#### 5. Database Setup

```bash
# Create database
createdb society_db

# Or with PostgreSQL CLI:
# psql -U postgres
# CREATE DATABASE society_db;

# Run migrations
alembic upgrade head

# Verify migrations
alembic current

# Create new migration (if schema changes)
alembic revision --autogenerate -m "Add new column to users"
```

#### 6. Start Development Server

```bash
# Using Uvicorn (auto-reload enabled)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or use the provided script
bash scripts/run_dev.sh

# Access:
# API: http://localhost:8000
# Docs (Swagger): http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

#### 7. Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=app

# Specific test file
pytest tests/test_auth.py

# Specific test function
pytest tests/test_auth.py::test_login_success

# With verbose output
pytest -v

# Stop on first failure
pytest -x
```

#### 8. Code Quality

```bash
# Format code
black .

# Sort imports
isort .

# Lint
flake8 .

# Type checking
mypy .

# Security check
bandit -r app/

# All checks together
pre-commit run --all-files
```

### Frontend Setup

#### 1. Navigate to Frontend

```bash
cd ../frontend
```

#### 2. Install Dependencies

```bash
npm install

# Or using Yarn
yarn install
```

#### 3. Environment Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with backend URL and API keys
# Key variables:
# - REACT_APP_API_URL=http://localhost:8000
# - REACT_APP_TELEGRAM_BOT_ID=your_bot_id
```

#### 4. Start Development Server

```bash
npm start

# Access: http://localhost:3000
# Auto-reload on file changes
```

#### 5. Running Tests

```bash
# All tests
npm test

# With coverage
npm test -- --coverage

# Watch mode
npm test -- --watch

# Specific test file
npm test Auth.test.jsx
```

#### 6. Build for Production

```bash
npm run build

# Optimized production build in build/ folder
```

#### 7. Code Quality

```bash
# Lint
npm run lint

# Format with Prettier
npm run format

# Both lint and format
npm run lint:fix
```

## Common Development Tasks

### Adding a New Backend Endpoint

1. **Create a new route** in `backend/app/api/routes/`:
```python
# backend/app/api/routes/my_feature.py
from fastapi import APIRouter, Depends
from app.schemas.my_schema import MySchemaRequest, MySchemaResponse
from app.services.my_service import MyService

router = APIRouter(prefix="/api/v1/my-feature", tags=["my-feature"])

@router.post("/create", response_model=MySchemaResponse)
async def create_item(
    request: MySchemaRequest,
    service: MyService = Depends()
):
    return await service.create(request)
```

2. **Add to main app** in `backend/app/main.py`:
```python
from app.api.routes import my_feature

app.include_router(my_feature.router)
```

3. **Create tests** in `backend/tests/test_my_feature.py`:
```python
def test_create_item(client, db_session):
    response = client.post("/api/v1/my-feature/create", json={...})
    assert response.status_code == 200
```

### Adding a New React Component

1. **Create component** in `frontend/src/components/`:
```jsx
// frontend/src/components/MyComponent.jsx
import React, { useState } from 'react';

function MyComponent({ props }) {
  return <div>My Component</div>;
}

export default MyComponent;
```

2. **Create test** in `frontend/src/components/`:
```jsx
// frontend/src/components/MyComponent.test.jsx
import { render, screen } from '@testing-library/react';
import MyComponent from './MyComponent';

test('renders component', () => {
  render(<MyComponent />);
  expect(screen.getByText('My Component')).toBeInTheDocument();
});
```

3. **Use component** in pages or other components:
```jsx
import MyComponent from '../components/MyComponent';
```

### Running Background Workers Locally

```bash
# Terminal 1: Backend API
cd backend
uvicorn app.main:app --reload

# Terminal 2: Telegram Listener Worker
cd backend
python -m app.workers.telegram_listener

# Terminal 3: Digest Generator (runs on schedule)
cd backend
python -m app.workers.digest_generator
```

### Working with Database Migrations

```bash
# Create migration (after model changes)
cd backend
alembic revision --autogenerate -m "description of changes"

# Review generated migration in alembic/versions/

# Apply migration
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# View migration history
alembic history

# Current migration status
alembic current
```

### Debugging

#### Backend Debugging

```bash
# Add breakpoint in code
import pdb; pdb.set_trace()

# Or use IPython in development
from IPython import embed; embed()

# Run with pdb
python -m pdb -m uvicorn app.main:app

# VS Code debugging - add to .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: FastAPI",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": ["app.main:app", "--reload"],
            "jinja": true,
            "cwd": "${workspaceFolder}/backend"
        }
    ]
}
```

#### Frontend Debugging

```bash
# Chrome DevTools - F12
# React DevTools extension recommended

# Console logging
console.log('debug:', variable);

# Debugger statement
debugger;

# VS Code debugging
# .vscode/launch.json for React
{
    "version": "0.2.0",
    "configurations": [
        {
            "type": "chrome",
            "request": "launch",
            "name": "Launch Chrome",
            "url": "http://localhost:3000",
            "webRoot": "${workspaceFolder}/frontend/src"
        }
    ]
}
```

## Environment Variables

### Backend (.env)

```
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/society_db

# Redis
REDIS_URL=redis://localhost:6379/0

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# Security
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# External APIs
TELEGRAM_BOT_TOKEN=your_telegram_token
TELEGRAM_BOT_ID=your_bot_id
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4

# Email
EMAIL_SERVICE=sendgrid  # or: smtp
EMAIL_FROM=noreply@society-app.com
SENDGRID_API_KEY=your_sendgrid_key

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Environment
ENVIRONMENT=development  # development, staging, production
CORS_ORIGINS=["http://localhost:3000"]
```

### Frontend (.env)

```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_TIMEOUT=30000
REACT_APP_TELEGRAM_BOT_ID=your_bot_id
REACT_APP_LOG_LEVEL=debug
```

## Useful Commands

```bash
# Backend

# Format and lint
black backend/ && isort backend/ && flake8 backend/

# Run all checks
pre-commit run --all-files

# Run tests with coverage
pytest backend/tests --cov=backend/app

# Database reset (DEV ONLY!)
dropdb society_db && createdb society_db && alembic upgrade head

# Fresh seed
python backend/scripts/seed_db.py

# Frontend

# Clean install
rm -rf node_modules package-lock.json && npm install

# Build and check
npm run build && npm run start

# Run linter and formatter
npm run lint:fix && npm run format

# Database

# Connect to PostgreSQL CLI
psql -U postgres -d society_db

# Useful queries
\dt                 # List tables
\d table_name       # Describe table
SELECT * FROM users;

# Common database commands
VACUUM;             # Optimize database
ANALYZE;            # Update statistics
```

## Troubleshooting

### Backend Issues

**Port 8000 already in use**
```bash
# Find process using port
lsof -i :8000
# Kill process
kill -9 <PID>
```

**Database connection refused**
```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432

# Restart PostgreSQL
# macOS
brew services restart postgresql

# Linux
sudo systemctl restart postgresql

# Windows
# Services → PostgreSQL → Restart
```

**Module not found errors**
```bash
# Ensure virtual env is activated
which python  # Should show venv path

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Frontend Issues

**Port 3000 already in use**
```bash
# Kill process on port 3000
lsof -i :3000
kill -9 <PID>
```

**npm modules issues**
```bash
# Clear cache
npm cache clean --force

# Reinstall
rm -rf node_modules package-lock.json
npm install
```

**CORS errors**
```bash
# Check backend CORS settings in .env
CORS_ORIGINS=["http://localhost:3000"]

# Restart backend after changes
```

## IDE Setup

### VS Code

**Recommended Extensions**:
- Python
- Pylance
- Black Formatter
- Prettier - Code formatter
- ESLint
- Thunder Client (for API testing)
- Thunder Client
- REST Client

**.vscode/settings.json**:
```json
{
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "ms-python.python",
  "[javascript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode",
    "editor.formatOnSave": true
  }
}
```

## Pre-commit Hooks

```bash
# Install pre-commit framework
pip install pre-commit

# Install git hooks
pre-commit install

# Run manually
pre-commit run --all-files

# Skip hooks (not recommended)
git commit --no-verify
```

## Resources

- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [React Documentation](https://react.dev/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)
- [Git Branching Strategy](../BRANCHING.md)
- [Commit Conventions](../COMMIT_CONVENTIONS.md)

## Need Help?

- Check existing [GitHub Issues](https://github.com/yourusername/society-app/issues)
- Review [Architecture Guide](./architecture.md)
- Ask in [Discussions](https://github.com/yourusername/society-app/discussions)
- Email: support@society-app.local
