# Society App - Community Platform

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/yourusername/society-app/actions)
[![License](https://img.shields.io/badge/license-MIT-blue)](./LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18.0%2B-blue)](https://react.dev/)
[![ISO 9001](https://img.shields.io/badge/ISO-9001:2015-green)]()
[![ISO 27001](https://img.shields.io/badge/ISO-27001:2022-green)]()

## Table of Contents

- [Overview](#overview)
- [Phase 1 Goals](#phase-1-goals)
- [Tech Stack](#tech-stack)
- [Features](#features)
- [Quick Start](#quick-start)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [Documentation](#documentation)
- [License](#license)

## Overview

**Society App** is a community platform designed for residential societies of 3500+ residents to facilitate communication, resource sharing, and demand-supply matching. 

### Phase 1: MVP - Daily Digests & Community Engagement
Monitors WhatsApp and Telegram groups in real-time, generates AI-powered daily digests, and provides a centralized platform for residents to share offers and requests.

## Phase 1 Goals

- ✅ Telegram group integration and message monitoring
- ✅ AI-powered daily digest generation (summarization)
- ✅ Web-based digest delivery system
- ✅ Demand-Supply matching engine (offers/requests)
- ✅ User authentication and role-based access control
- ✅ Mobile-responsive PWA interface
- ✅ PostgreSQL database with ISO 27001 security practices
- ✅ CI/CD pipeline with automated testing

## Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Backend** | Python (FastAPI) | 3.10+ |
| **Frontend** | React + PWA | 18.0+ |
| **Database** | PostgreSQL | 14+ |
| **Message Queue** | Redis | 7+ |
| **AI/LLM** | OpenAI API | Latest |
| **Authentication** | JWT + OAuth2 | - |
| **Containerization** | Docker | 20+ |
| **CI/CD** | GitHub Actions | - |

## Features

### Phase 1 (Current)
- **Telegram Integration**: Real-time group monitoring and message ingestion
- **AI Digest Generation**: Daily summaries using GPT-4/Claude
- **Web Dashboard**: View digests, browse offers/requests
- **Demand-Supply Module**: Post and search offers/requests
- **User Management**: Role-based access (Admin, Moderator, Resident)

### Future Phases
- WhatsApp integration
- Mobile app (React Native)
- Advanced analytics and insights
- Event management
- Payment integration

## Quick Start

### Prerequisites

- Python 3.10 or higher
- Node.js 16 or higher
- PostgreSQL 14 or higher
- Docker & Docker Compose (optional)
- Git

### Installation

#### Clone and Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/society-app.git
cd society-app

# Create develop branch (if not exists)
git checkout -b develop origin/develop || git checkout develop

# Create feature branch
git checkout -b feature/your-feature-name
```

#### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Copy environment variables
cp .env.example .env
# Edit .env with your configuration

# Start development server
npm start
```

#### Docker Setup (Recommended)

```bash
# Build and start all services
docker-compose up -d

# Run migrations
docker-compose exec backend alembic upgrade head

# Access the app
# Frontend: http://localhost:3000
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

## Usage

### Starting the Application

**Development Mode:**
```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
uvicorn main:app --reload

# Terminal 2 - Frontend
cd frontend
npm start
```

**Production Mode:**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Configuration

See [.env.example](.env.example) for required environment variables.

## Project Structure

```
society-app/
├── backend/                          # FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # Entry point
│   │   ├── config.py                 # Configuration
│   │   ├── dependencies.py           # Dependency injection
│   │   ├── api/
│   │   │   ├── routes/               # API endpoints
│   │   │   │   ├── auth.py
│   │   │   │   ├── digests.py
│   │   │   │   ├── demand_supply.py
│   │   │   │   └── telegram.py
│   │   │   └── v1/
│   │   ├── core/
│   │   │   ├── security.py           # Authentication & authorization
│   │   │   ├── config.py
│   │   │   └── constants.py
│   │   ├── db/
│   │   │   ├── base.py               # SQLAlchemy base
│   │   │   ├── session.py            # Database session
│   │   │   └── models.py             # Data models
│   │   ├── schemas/                  # Pydantic schemas
│   │   │   ├── user.py
│   │   │   ├── digest.py
│   │   │   └── offer_request.py
│   │   ├── services/                 # Business logic
│   │   │   ├── ai_digest.py          # AI summarization
│   │   │   ├── telegram_bot.py       # Telegram integration
│   │   │   ├── auth.py               # Authentication service
│   │   │   └── matching.py           # Demand-supply matching
│   │   ├── workers/                  # Async tasks
│   │   │   ├── digest_generator.py
│   │   │   └── telegram_listener.py
│   │   └── utils/
│   │       ├── logger.py
│   │       ├── exceptions.py
│   │       └── helpers.py
│   ├── tests/                        # Unit & integration tests
│   │   ├── test_auth.py
│   │   ├── test_digests.py
│   │   └── conftest.py
│   ├── migrations/                   # Alembic migrations
│   ├── requirements.txt
│   ├── .env.example
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── setup.cfg
│
├── frontend/                         # React PWA
│   ├── public/
│   │   ├── index.html
│   │   ├── manifest.json             # PWA manifest
│   │   └── favicon.ico
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/               # Reusable components
│   │   │   │   ├── Header.jsx
│   │   │   │   ├── Footer.jsx
│   │   │   │   └── Navbar.jsx
│   │   │   ├── Digest/
│   │   │   │   ├── DigestList.jsx
│   │   │   │   └── DigestDetail.jsx
│   │   │   ├── DemandSupply/
│   │   │   │   ├── OfferList.jsx
│   │   │   │   ├── RequestList.jsx
│   │   │   │   └── CreateOffer.jsx
│   │   │   └── Auth/
│   │   │       ├── Login.jsx
│   │   │       └── Register.jsx
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Digests.jsx
│   │   │   ├── Marketplace.jsx
│   │   │   └── Profile.jsx
│   │   ├── services/
│   │   │   └── api.js                # API client
│   │   ├── utils/
│   │   │   ├── auth.js
│   │   │   └── constants.js
│   │   ├── App.jsx
│   │   └── index.js
│   ├── public/
│   ├── package.json
│   ├── .env.example
│   ├── .eslintrc.json
│   ├── .prettierrc
│   └── Dockerfile
│
├── docs/                             # Documentation
│   ├── architecture.md               # System design
│   ├── developer-guide.md            # Setup & development
│   ├── user-guide.md                 # End-user guide
│   └── api-reference.md              # API documentation
│
├── .github/
│   ├── workflows/
│   │   └── ci.yml                    # CI/CD pipeline
│   └── ISSUE_TEMPLATE/
│       ├── bug_report.md
│       └── feature_request.md
│
├── .gitignore
├── .pre-commit-config.yaml           # Pre-commit hooks
├── docker-compose.yml                # Multi-container setup
├── README.md                         # This file
├── BRANCHING.md                      # Git branching strategy
├── COMMIT_CONVENTIONS.md             # Commit message standards
├── CONTRIBUTING.md                   # Contribution guidelines
├── CHANGELOG.md                      # Version history
├── PROJECT_BOARD.md                  # Phase 1 tasks
├── LICENSE                           # MIT License
└── .env.example                      # Environment variables template
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines on:
- Reporting bugs
- Submitting feature requests
- Code standards
- Pull request process

## Documentation

- **[Architecture Guide](./docs/architecture.md)** - System design and components
- **[Developer Guide](./docs/developer-guide.md)** - Local setup and testing
- **[User Guide](./docs/user-guide.md)** - Feature documentation
- **[Branching Strategy](./BRANCHING.md)** - Git workflow
- **[Commit Conventions](./COMMIT_CONVENTIONS.md)** - Commit message format
- **[Project Board](./PROJECT_BOARD.md)** - Phase 1 roadmap
- **[Changelog](./CHANGELOG.md)** - Release history

## Standards & Compliance

This project adheres to:
- **ISO 9001:2015** - Quality Management System
- **ISO/IEC 12207** - Software and systems engineering lifecycle processes
- **ISO/IEC 27001:2022** - Information security management
- **ISO/IEC 25010** - Software product quality model

## License

This project is licensed under the MIT License - see [LICENSE](./LICENSE) file for details.

## Support

For questions or issues:
- 📧 Email: support@society-app.local
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/society-app/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/society-app/discussions)

---

**Made with ❤️ for communities**
