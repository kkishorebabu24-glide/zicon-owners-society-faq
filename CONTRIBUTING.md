# Contributing to Society App

Thank you for your interest in contributing to the Society App project! This document provides guidelines and instructions for participating in our community.

## Code of Conduct

Our project adheres to a Code of Conduct to ensure a welcoming and inclusive environment. By participating, you are expected to:
- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

## How to Contribute

### Reporting Bugs

Before creating a bug report, please check the [issue list](https://github.com/yourusername/society-app/issues) as you might find out that you don't need to create one.

When reporting a bug, include as many details as possible:
- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples to demonstrate the steps**
- **Describe the behavior you observed after following the steps**
- **Explain which behavior you expected to see instead and why**
- **Include screenshots if possible**
- **Include your environment (OS, Python version, browser, etc.)**

See [bug_report.md](.github/ISSUE_TEMPLATE/bug_report.md) for the template.

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:
- **A clear and descriptive title**
- **A step-by-step description of the suggested enhancement**
- **Specific examples to demonstrate the steps**
- **Describe the current behavior and what's missing**
- **Explain why this enhancement would be useful**

See [feature_request.md](.github/ISSUE_TEMPLATE/feature_request.md) for the template.

### Pull Requests

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/society-app.git
   cd society-app
   ```

2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature develop
   ```

3. **Make Your Changes**
   - Follow the [Commit Conventions](./COMMIT_CONVENTIONS.md)
   - Keep commits small and focused
   - Add tests for new functionality
   - Update documentation as needed

4. **Test Your Changes**
   ```bash
   # Backend
   cd backend
   pytest tests/
   black .
   flake8 .
   
   # Frontend
   cd frontend
   npm test
   npm run lint
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature
   ```
   - Go to GitHub and create a Pull Request
   - Link any related issues: `Closes #123`
   - Provide a clear description of changes

6. **Address Review Feedback**
   - Make requested changes
   - Push updates to the same branch
   - Comment on suggestions if you have questions

## Development Setup

### Prerequisites
- Python 3.10+
- Node.js 16+
- PostgreSQL 14+
- Docker (optional)

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env
npm start
```

## Coding Standards

### Python Backend

- **Style**: Follow [PEP 8](https://pep8.org/) using Black formatter
- **Type Hints**: Use type hints for all functions
- **Documentation**: Write docstrings for all functions and classes
- **Testing**: Aim for >80% code coverage
- **Imports**: Sort using isort

Format:
```bash
black backend/
isort backend/
```

Lint:
```bash
flake8 backend/
mypy backend/
pylint backend/
```

### React Frontend

- **Style**: Follow [Airbnb style guide](https://github.com/airbnb/javascript)
- **Components**: Use functional components with hooks
- **Documentation**: Add JSDoc comments for components
- **Testing**: Write tests for all components (>80% coverage)
- **Formatting**: Use Prettier

Format:
```bash
cd frontend
npx prettier --write src/
npx eslint --fix src/
```

Lint:
```bash
npm run lint
```

### Commit Messages

Follow [Conventional Commits](./COMMIT_CONVENTIONS.md):

```
feat(scope): description
fix(scope): description
docs: description
test: description
refactor(scope): description
```

Examples:
- `feat(telegram): add group message listener`
- `fix(digest): correct timestamp formatting`
- `docs: update installation guide`
- `test(auth): add login endpoint tests`

## Documentation

- **README.md**: Project overview and quick start
- **docs/architecture.md**: System design and components
- **docs/developer-guide.md**: Development setup and workflow
- **docs/user-guide.md**: Feature documentation for end-users
- **BRANCHING.md**: Git branching strategy
- **COMMIT_CONVENTIONS.md**: Commit message format
- **CHANGELOG.md**: Version history

When making changes:
1. Update relevant documentation
2. Add examples if applicable
3. Update table of contents if adding new sections
4. Check for outdated information

## Testing Guidelines

### Backend Tests
```bash
cd backend
pytest tests/ -v --cov=app
```

Test structure:
```
tests/
├── test_auth.py
├── test_digests.py
├── test_telegram_bot.py
├── conftest.py
└── fixtures/
```

### Frontend Tests
```bash
cd frontend
npm test -- --coverage --watchAll=false
```

Test structure:
```
src/
├── components/
│   ├── Auth/
│   │   ├── Login.jsx
│   │   └── Login.test.jsx
│   └── Digest/
│       ├── DigestList.jsx
│       └── DigestList.test.jsx
```

## Review Process

All PRs require:
1. ✅ **Code review** - At least 2 approvals
2. ✅ **Tests passing** - All CI checks must pass
3. ✅ **Documentation** - Updated if needed
4. ✅ **No conflicts** - Resolved before merge

## Release Process

1. Create a release branch: `release/v1.0.0`
2. Update version in all files
3. Update CHANGELOG.md
4. Create PR to main
5. After merge, create git tag: `git tag -a v1.0.0 -m "Release v1.0.0"`
6. Create GitHub Release with changelog

## Getting Help

- 📚 **Documentation**: Check [docs/](./docs/)
- 🐛 **Issues**: Search [GitHub Issues](https://github.com/yourusername/society-app/issues)
- 💬 **Discussions**: Ask in [GitHub Discussions](https://github.com/yourusername/society-app/discussions)
- 📧 **Email**: support@society-app.local

## License

By contributing to Society App, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to make Society App better! 🎉
