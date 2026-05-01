# Testing Quickstart Guide

This guide explains how to run the complete test suite for the Home Food Sellers Platform locally.

## Prerequisites

### System Requirements
- **Python**: 3.10 or higher
- **Node.js**: 18 or higher
- **Docker**: For running test databases
- **Git**: For version control

### Environment Setup
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd home-food-sellers-platform
   ```

2. **Start test infrastructure**
   ```bash
   docker-compose up -d postgres redis
   ```

3. **Set up Python environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt -r requirements-dev.txt
   ```

4. **Set up Node.js environment**
   ```bash
   cd ../frontend
   npm install
   ```

## Test Categories

### 1. Backend Unit Tests

**Purpose**: Test individual functions and components in isolation

**Command**:
```bash
cd backend
pytest tests/unit/ -v --cov=app --cov-report=html
```

**Expected Output**:
```
========================= test session starts =========================
tests/unit/test_auth.py::test_password_hashing PASSED
tests/unit/test_models.py::test_user_creation PASSED
...
----------- coverage: platform linux, python 3.10.0-final-0 -----------
Name          Stmts   Miss  Cover
---------------------------------
app/__init__.py     10      0   100%
app/auth.py         45      2    96%
...
========================= 25 passed in 2.34s ========================
```

### 2. Backend Integration Tests

**Purpose**: Test API endpoints and database interactions

**Setup**:
```bash
cd backend
cp .env.example .env.test
# Edit .env.test with test database credentials
```

**Command**:
```bash
cd backend
pytest tests/integration/ -v --tb=short
```

**Expected Output**:
```
========================= test session starts =========================
tests/integration/test_auth_api.py::test_user_registration PASSED
tests/integration/test_menu_api.py::test_create_menu_item PASSED
...
========================= 15 passed in 12.45s ========================
```

### 3. Frontend Unit Tests

**Purpose**: Test React components and utilities

**Command**:
```bash
cd frontend
npm test -- --coverage --watchAll=false
```

**Expected Output**:
```
PASS src/components/MenuCard.test.js
PASS src/utils/validation.test.js
...
=========================== Coverage summary ===========================
Statements   : 85.2%
Branches     : 78.5%
Functions    : 92.1%
Lines        : 84.7%
===================================================================
Test Suites: 12 passed, 12 total
Tests:       45 passed, 45 total
```

### 4. End-to-End Tests

**Purpose**: Test complete user workflows

**Setup**:
```bash
# Start the full application stack
docker-compose up -d
cd backend && uvicorn main:app --host 0.0.0.0 --port 8000 &
cd frontend && npm start &
```

**Command**:
```bash
cd frontend
npx playwright test
```

**Expected Output**:
```
Running 8 tests using 2 workers
  ✓ user-registration.spec.js:5:1 › User Registration › Successful registration (4.2s)
  ✓ menu-management.spec.js:3:1 › Menu Management › Create menu item (3.1s)
  ✓ order-placement.spec.js:4:1 › Order Placement › Complete order flow (6.8s)
  ...
  8 passed (42.3s)
```

## Performance Testing

### Load Testing with Locust

**Setup**:
```bash
pip install locust
```

**Command**:
```bash
cd backend
locust -f tests/performance/locustfile.py --host=http://localhost:8000
```

**Access**: Open http://localhost:8089 in browser

### API Load Testing with k6

**Setup**:
```bash
# Install k6 from https://k6.io/docs/get-started/installation/
```

**Command**:
```bash
cd backend
k6 run tests/performance/api-load-test.js
```

## Security Testing

### Static Security Analysis

**Backend**:
```bash
cd backend
bandit -r app/
```

**Frontend**:
```bash
cd frontend
npm audit
```

### API Security Testing

**Setup**:
```bash
pip install owasp-zap
# Or use the OWASP ZAP GUI
```

## Test Data Management

### Generate Test Data

**Command**:
```bash
cd backend
python ../docs/testing/test-data-generation.py
```

**This creates**:
- 50 test residents (20 sellers, 30 buyers)
- 200+ menu items across categories
- 100 orders with various statuses
- Ratings and reviews

### Reset Test Database

**Command**:
```bash
cd backend
# Drop and recreate database
psql -h localhost -U postgres -c "DROP DATABASE IF EXISTS test_db;"
psql -h localhost -U postgres -c "CREATE DATABASE test_db;"

# Run migrations
alembic upgrade head

# Generate fresh test data
python ../docs/testing/test-data-generation.py
```

## Code Quality Checks

### Backend Linting

**Command**:
```bash
cd backend
black --check .
isort --check-only .
flake8 .
mypy .
```

### Frontend Linting

**Command**:
```bash
cd frontend
npm run lint
npx prettier --check src/
```

## Continuous Integration

### Run All Tests Locally

**Command**:
```bash
# From project root
./scripts/run-all-tests.sh
```

### CI Pipeline Simulation

**Command**:
```bash
# Run the same checks as GitHub Actions
docker build -f backend/Dockerfile -t backend-test backend/
docker build -f frontend/Dockerfile -t frontend-test frontend/
```

## Debugging Failed Tests

### Common Issues

1. **Database Connection Failed**
   ```bash
   # Check if PostgreSQL is running
   docker ps | grep postgres

   # Check database logs
   docker logs <postgres-container-id>
   ```

2. **Port Already in Use**
   ```bash
   # Find process using port
   lsof -i :8000

   # Kill process
   kill -9 <PID>
   ```

3. **Test Data Issues**
   ```bash
   # Reset and regenerate test data
   cd backend
   python ../docs/testing/test-data-generation.py
   ```

### Test Debugging

**Run specific test with verbose output**:
```bash
cd backend
pytest tests/integration/test_auth_api.py::test_user_registration -v -s
```

**Run tests with coverage details**:
```bash
cd backend
pytest tests/ --cov=app --cov-report=html
# Open htmlcov/index.html in browser
```

## Test Reports

### Generate Coverage Reports

**Backend**:
```bash
cd backend
pytest tests/ --cov=app --cov-report=html --cov-report=xml
```

**Frontend**:
```bash
cd frontend
npm test -- --coverage --coverageReporters=html
```

### View Test Results

- **Coverage Reports**: Open `htmlcov/index.html` or `coverage/lcov-report/index.html`
- **Playwright Reports**: `npx playwright show-report`
- **Allure Reports**: `allure serve allure-results/`

## Performance Benchmarks

### Target Metrics

| Metric | Target | Command to Check |
|--------|--------|------------------|
| API Response Time | <500ms | `curl -w "@curl-format.txt" http://localhost:8000/api/menu` |
| Page Load Time | <3s | Browser DevTools or Lighthouse |
| Concurrent Users | 500+ | Locust load test |
| Memory Usage | <512MB | `docker stats` |

## Troubleshooting

### Environment Issues

**Python virtual environment not activating**:
```bash
# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

**Node modules installation fails**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Test Flakiness

**Database state issues**:
```bash
# Use test fixtures with proper cleanup
@pytest.fixture(autouse=True)
def clean_db(db_session):
    db_session.query(Order).delete()
    db_session.query(MenuItem).delete()
    db_session.commit()
```

**Timing issues in E2E tests**:
```bash
# Add proper waits
await page.waitForSelector('.menu-item', { timeout: 5000 });
```

## Contributing to Tests

### Adding New Tests

1. **Unit Tests**: Add to `backend/tests/unit/` or `frontend/src/__tests__/`
2. **Integration Tests**: Add to `backend/tests/integration/`
3. **E2E Tests**: Add to `frontend/tests/e2e/`

### Test Naming Convention

- Files: `test_*.py` or `*.test.js`
- Functions: `test_*`
- Classes: `Test*`

### Test Documentation

```python
def test_user_registration_success():
    """
    Test successful user registration with valid data.

    Verifies:
    - User is created in database
    - OTP is sent (mocked)
    - Response contains success message
    """
```

## Getting Help

- Check existing issues in GitHub
- Review test logs for error details
- Run tests with `-v` flag for verbose output
- Check database state during test execution

## Next Steps

After running all tests successfully:

1. **Review Coverage Reports**: Ensure >90% backend, >80% frontend coverage
2. **Performance Testing**: Run load tests with target user counts
3. **Security Review**: Address any security scan findings
4. **UAT Preparation**: Use test data for user acceptance testing

---

**Last Updated**: April 18, 2026
**Test Framework Versions**:
- pytest: 7.4+
- Jest: 29.5+
- Playwright: 1.35+
- Locust: 2.15+