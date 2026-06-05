# Society App - Architecture Analysis & Real-Time Updates Implementation Plan

## Executive Summary

The Society App has a **solid foundation with a complete infrastructure setup** but is currently at the **skeleton/stub phase**. All API routes are empty (TODO), database models are undefined, and frontend is a basic health check page. This document outlines the current structure and modifications needed for real-time updates.

---

## 1. CURRENT BACKEND STRUCTURE

### 1.1 FastAPI Application Setup (`backend/app/main.py`)

**Current Status:** ✅ Initialized, routes commented out
- FastAPI app created with title and version
- CORS middleware enabled for `http://localhost:3000` and `http://localhost:8000`
- GZip middleware for compression
- Health check endpoint (`/health`) - **ACTIVE**
- Root endpoint (`/`) - **ACTIVE**
- Route includes **COMMENTED OUT** (lines 52-57):
  ```python
  # TODO: Add route includes
  # from app.api.routes import auth, digests, demand_supply, telegram
  # app.include_router(auth.router)
  # app.include_router(digests.router)
  # app.include_router(demand_supply.router)
  # app.include_router(telegram.router)
  ```

**What needs modification:**
- Uncomment and enable route includes
- Add WebSocket endpoint registration (for real-time updates)
- Add event handlers for startup/shutdown (to initialize Redis connections, WebSocket managers)

### 1.2 API Routes Structure (`backend/app/api/routes/`)

All four route files are **skeleton implementations with TODO comments**:

#### `auth.py`
```
Prefix: /api/v1/auth
Planned endpoints (not implemented):
  - POST /register
  - POST /login
  - POST /refresh
  - POST /logout
  - GET /me
```

#### `demand_supply.py` (Requests & Offers)
```
Prefix: /api/v1/marketplace
Planned endpoints (not implemented):
  - GET /offers (list all offers)
  - POST /offers (create new offer)
  - GET /offers/{id} (get offer details)
  - PUT /offers/{id} (update offer)
  - DELETE /offers/{id} (delete offer)
  - GET /requests (list all requests)
  - POST /requests (create new request)
  - GET /requests/{id} (get request details)
  - GET /matches (get matching offers/requests)
```

#### `digests.py`
```
Prefix: /api/v1/digests
Planned endpoints (not implemented):
  - GET /digests (list digests)
  - GET /digests/{id} (get digest details)
  - GET /digests/user/{user_id} (user's digests)
  - POST /digests (admin only, create digest)
```

#### `telegram.py`
```
Prefix: /api/v1/telegram
Planned endpoints (not implemented):
  - POST /webhook (receive Telegram updates)
  - POST /config (configure bot groups)
  - GET /groups (list configured groups)
```

**What needs modification:**
- Implement all endpoints with proper request/response models
- Add WebSocket endpoint in `demand_supply.py` for real-time offer/request updates
- Add WebSocket endpoint in `digests.py` for real-time digest delivery notifications
- Add pub/sub integration with Redis for cross-client broadcasts

### 1.3 Database Models (`backend/app/db/models.py`)

**Current Status:** ⚠️ **COMPLETELY EMPTY** - Only TODO comments exist

Models needed:
```
- User (auth, roles, preferences)
- TelegramGroup (bot group configurations)
- Message (Telegram messages)
- Digest (daily summaries)
- Offer (marketplace offers)
- Request (marketplace requests)
- Match (offer-request matches)
- UserPreferences (notification settings)
```

**What needs modification:**
- Define SQLAlchemy ORM models with proper relationships
- Add indexes on frequently queried columns (user_id, group_id, created_at, updated_at)
- Include timestamps (created_at, updated_at) for audit trails
- Add soft-delete flags for GDPR compliance

### 1.4 Configuration (`backend/app/config.py`)

**Current Status:** ✅ Well-defined with feature flags

Available settings:
- Database URL (PostgreSQL)
- Redis URL
- JWT secrets and tokens
- CORS origins
- External API keys (Telegram, OpenAI, SendGrid)
- Feature flags:
  - `TELEGRAM_INTEGRATION_ENABLED`
  - `AI_DIGEST_ENABLED`
  - `DEMAND_SUPPLY_ENABLED`

**What needs modification:**
- Add WebSocket configuration (connection limits, timeout, heartbeat intervals)
- Add Redis pub/sub channel names
- Add rate limiting settings
- Add real-time update broadcast settings

### 1.5 Dependencies (`backend/requirements.txt`)

**Current Status:** ✅ Comprehensive dependency list

**Key packages available:**
- `fastapi` + `uvicorn` - Web framework
- `sqlalchemy` + `psycopg2-binary` + `alembic` - ORM and migrations
- `redis` - Cache and pub/sub
- `pydantic` - Data validation
- `python-telegram-bot` - Telegram integration
- `python-jose` + `passlib` + `PyJWT` - Authentication
- `httpx` - Async HTTP client
- `openai` - AI digest generation

**What's MISSING for real-time updates:**
- ❌ `websockets` or `python-socketio` - WebSocket support
- ❌ `fastapi-socketio` - FastAPI WebSocket integration
- ❌ `fastapi[websockets]` - Built-in WebSocket support in FastAPI

**Recommendation:** Add to requirements.txt:
```
websockets==12.0
fastapi-socketio==0.0.10  # Optional, if using Socket.IO
```

---

## 2. CURRENT FRONTEND STRUCTURE

### 2.1 React Application (`frontend/src/App.jsx`)

**Current Status:** 🟡 Basic health check UI only

Current functionality:
- Fetches and displays backend health status
- Shows API endpoint URL
- Displays health check JSON response
- Has "Refresh" button and link to API docs
- Lists TODO items for next work phases

**Components present:**
- Single `App` component (monolithic)
- Basic CSS styling in `index.css`

**What needs modification:**
- Break into modular components:
  - `pages/AuthPage` (login/register)
  - `pages/MarketplacePage` (requests/offers list)
  - `pages/DigestsPage` (view digests)
  - `pages/TelegramSettingsPage` (group config)
  - `components/OfferCard` (display single offer)
  - `components/RequestCard` (display single request)
  - `components/DigestCard` (display single digest)
- Implement routing with React Router (already in dependencies)
- Add Redux store for state management (already in dependencies)
- Add authentication context/flow

### 2.2 Package.json Dependencies

**Current Status:** ✅ Good foundation for frontend

**Available frameworks:**
- `react@18.2.0` + `react-dom`
- `react-router-dom@6.20.0` - Routing
- `@reduxjs/toolkit@1.9.7` + `react-redux@8.1.3` - State management
- `@mui/material@5.14.0` - UI components library
- `axios@1.6.0` - HTTP client
- `date-fns@2.30.0` - Date formatting

**What's MISSING for real-time updates:**
- ❌ `socket.io-client` - WebSocket client
- ❌ `ws` - WebSocket library

**Recommendation:** Add to package.json:
```json
"socket.io-client": "^4.7.2"  // For Socket.IO real-time updates
// OR
"ws": "^8.14.2"               // For native WebSocket support
```

### 2.3 Application Structure

```
frontend/src/
├── App.jsx           (main component - needs modularization)
├── index.js          (entry point)
├── index.css         (global styles)
└── (missing):
    ├── pages/        (page components)
    ├── components/   (reusable components)
    ├── store/        (Redux store setup)
    ├── services/     (API client functions)
    ├── utils/        (helper functions)
    └── hooks/        (custom React hooks)
```

---

## 3. INFRASTRUCTURE & DEPLOYMENT

### 3.1 Docker Compose Setup (`docker-compose.yml`)

**Current Status:** ✅ Complete and well-configured

Services:
- **PostgreSQL 17** - Main database
- **Redis 7** - Cache and pub/sub
- **FastAPI Backend** - Hot reload enabled
- **React Frontend** - Hot reload enabled

**Features:**
- Health checks configured for all services
- Network isolation (`society-network`)
- Volume mounts for development hot reload
- Environment variable configuration via `.env` file

**What needs modification:**
- Add WebSocket proxy configuration (Nginx if needed for production)
- Add message queue worker service for background tasks (Celery + Redis)

---

## 4. REAL-TIME UPDATES ARCHITECTURE

### 4.1 Current Real-Time Support: ❌ NONE

No WebSocket implementation exists. Current flow is **HTTP polling only**:
```
Frontend (HTTP GET) → Backend (REST API) → Database
                    ↓ (Response)
Frontend (displays data)
```

### 4.2 Proposed Real-Time Architecture

#### Option A: Native WebSocket + Redis Pub/Sub
```
┌─────────────────┐         ┌──────────────┐
│    Frontend     │◄────────│  WebSocket   │
│  (Socket.IO or │         │   Server     │
│   Native WS)    │────────►│              │
└─────────────────┘         └──────────────┘
                                    ▲
                                    │ Subscribe
                            ┌───────┴─────────┐
                            │   Redis Pub/Sub  │
                            │  Channels:       │
                            │  - digests       │
                            │  - offers        │
                            │  - requests      │
                            │  - matches       │
                            └──────────────────┘
                                    ▲
                                    │ Publish
                            ┌───────┴──────────┐
                            │   API Endpoints   │
                            │   & Services      │
                            └───────────────────┘
```

**Components needed:**
1. **Backend WebSocket Manager** (`backend/app/api/websocket_manager.py`)
   - Manage active WebSocket connections
   - Handle client subscriptions
   - Broadcast messages from Redis pub/sub

2. **Redis Publishers** (in each service)
   - Publish to channels when data changes
   - Channels: `digests`, `offers`, `requests`, `matches`

3. **WebSocket Endpoints** (in route files)
   - `/api/v1/digests/ws` - Real-time digest notifications
   - `/api/v1/marketplace/ws` - Real-time offer/request updates

4. **Frontend WebSocket Client** (`frontend/src/services/websocket.js`)
   - Connect to WebSocket endpoint
   - Subscribe to relevant channels
   - Update Redux state on new messages
   - Reconnect on connection loss

### 4.3 Real-Time Event Types

```
Events needed:

1. DIGEST_CREATED
   {
     event: "digest_created",
     data: { id, title, summary, created_at, pdf_url }
   }

2. OFFER_CREATED / OFFER_UPDATED / OFFER_DELETED
   {
     event: "offer_created",
     data: { id, user_id, title, category, price, status, created_at }
   }

3. REQUEST_CREATED / REQUEST_UPDATED / REQUEST_DELETED
   {
     event: "request_created",
     data: { id, user_id, title, category, budget, status, created_at }
   }

4. MATCH_FOUND
   {
     event: "match_found",
     data: { offer_id, request_id, match_score, matched_at }
   }

5. USER_NOTIFICATION
   {
     event: "notification",
     data: { id, type, title, message, action_url, read }
   }
```

---

## 5. IMPLEMENTATION ROADMAP

### Phase 1: Database & Models ⬜ (REQUIRED FIRST)
- [ ] Define SQLAlchemy models (User, Digest, Offer, Request, etc.)
- [ ] Create Alembic migrations
- [ ] Set up database relationships and indexes

### Phase 2: Authentication ⬜
- [ ] Implement auth routes (register, login, token refresh)
- [ ] Add JWT token generation and validation
- [ ] Create user authentication middleware

### Phase 3: REST API for CRUD ⬜
- [ ] Implement demand_supply routes (GET/POST/PUT/DELETE offers & requests)
- [ ] Implement digests routes (GET digests, create digest)
- [ ] Implement basic Telegram webhook handler
- [ ] Add request/response validation with Pydantic models

### Phase 4: WebSocket Real-Time Updates ⬜
- [ ] Add WebSocket dependencies to requirements.txt
- [ ] Create WebSocket manager in backend
- [ ] Implement Redis pub/sub integration
- [ ] Add WebSocket endpoints for digests and marketplace
- [ ] Add connection lifecycle management (connect, disconnect, errors)

### Phase 5: Frontend Components & State ⬜
- [ ] Create Redux store structure
- [ ] Build page components (Auth, Digests, Marketplace)
- [ ] Build reusable card components
- [ ] Implement routing and navigation

### Phase 6: Frontend WebSocket Integration ⬜
- [ ] Create WebSocket service client
- [ ] Connect Redux to WebSocket events
- [ ] Implement real-time data updates in UI
- [ ] Add connection status indicator

### Phase 7: Background Tasks ⬜
- [ ] Set up Celery for background jobs
- [ ] Implement AI digest generation worker
- [ ] Implement Telegram message monitoring worker

---

## 6. WHAT NEEDS TO BE MODIFIED

### Backend Changes Required

| File | Change | Priority |
|------|--------|----------|
| `backend/app/db/models.py` | Define all SQLAlchemy models | 🔴 CRITICAL |
| `backend/app/main.py` | Uncomment route includes, add WebSocket endpoints | 🟠 HIGH |
| `backend/app/api/routes/auth.py` | Implement all auth endpoints | 🟠 HIGH |
| `backend/app/api/routes/demand_supply.py` | Implement CRUD endpoints, add WebSocket | 🟠 HIGH |
| `backend/app/api/routes/digests.py` | Implement endpoints, add WebSocket | 🟠 HIGH |
| `backend/app/api/routes/telegram.py` | Implement webhook handler | 🟠 HIGH |
| `backend/app/config.py` | Add WebSocket config, Redis channels | 🟡 MEDIUM |
| `backend/requirements.txt` | Add websockets package | 🟠 HIGH |
| (New) `backend/app/api/websocket_manager.py` | WebSocket connection manager | 🟠 HIGH |
| (New) `backend/app/services/` | Business logic services | 🟠 HIGH |
| (New) `backend/app/schemas/` | Pydantic request/response models | 🟠 HIGH |

### Frontend Changes Required

| File | Change | Priority |
|------|--------|----------|
| `frontend/package.json` | Add socket.io-client | 🟠 HIGH |
| `frontend/src/App.jsx` | Refactor into routing structure | 🟠 HIGH |
| (New) `frontend/src/pages/` | Create page components | 🟠 HIGH |
| (New) `frontend/src/components/` | Create reusable components | 🟠 HIGH |
| (New) `frontend/src/store/` | Redux store setup | 🟠 HIGH |
| (New) `frontend/src/services/` | API client, WebSocket client | 🟠 HIGH |
| (New) `frontend/src/hooks/` | Custom React hooks | 🟡 MEDIUM |

### Infrastructure Changes Required

| File | Change | Priority |
|------|--------|----------|
| `backend/requirements.txt` | Add websockets==12.0 | 🟠 HIGH |
| `docker-compose.yml` | No major changes (Redis already available) | 🟢 LOW |
| `.env` | Add WebSocket configuration | 🟡 MEDIUM |

---

## 7. KEY TECHNICAL DECISIONS

### Real-Time Update Strategy
- **Chosen: Redis Pub/Sub + Native WebSocket** (no external dependencies beyond `websockets`)
- Why: Simple, scalable, already have Redis in stack
- Alternative: Socket.IO (adds dependency but includes fallbacks)

### Database ORM
- **Chosen: SQLAlchemy 2.0** (already in requirements)
- Async support needed: `sqlalchemy[asyncio]` + `asyncpg` (PostgreSQL async driver)

### Frontend State Management
- **Chosen: Redux + React Router** (already in package.json)
- Redux for centralized state, hooks for local component state

### API Validation
- **Chosen: Pydantic v2** (already in requirements)
- Request/response models in `schemas/` directory

---

## 8. TESTING & QUALITY ASSURANCE

**Missing from current setup:**
- No test files or test frameworks activated
- No CI/CD pipeline visible
- No linting/formatting configured for backend

**Needed:**
- Backend: pytest, pytest-asyncio for async test support
- Frontend: Jest, React Testing Library (already in devDependencies)
- GitHub Actions for CI/CD (referenced in README badges but not implemented)

---

## 9. SECURITY CONSIDERATIONS

**Current security measures:**
- ✅ JWT authentication planned
- ✅ CORS configured
- ✅ Password hashing with bcrypt planned
- ✅ HTTPS assumed in production

**Needed for real-time updates:**
- ✅ WebSocket authentication (validate JWT on WS upgrade)
- ❌ Rate limiting on WebSocket connections
- ❌ Input validation on WebSocket messages
- ❌ Connection limits per user
- ❌ Proper error handling (no stack traces to client)

---

## SUMMARY CHECKLIST

### ✅ Already In Place
- [x] FastAPI framework initialized
- [x] PostgreSQL + Redis infrastructure
- [x] CORS middleware
- [x] Docker Compose with hot reload
- [x] Configuration management
- [x] React project setup with Material-UI
- [x] Package dependencies mostly ready

### ❌ Still Needed
- [ ] Database models (CRITICAL)
- [ ] API route implementations (CRITICAL)
- [ ] WebSocket support (websockets package)
- [ ] WebSocket endpoints and managers
- [ ] Redis pub/sub integration
- [ ] Frontend component structure
- [ ] Redux store setup
- [ ] WebSocket client in frontend
- [ ] Authentication flow
- [ ] Background task workers
- [ ] Unit and integration tests
- [ ] Error handling and logging

---

## NEXT STEPS

1. **Start with Database Models** - Define User, Digest, Offer, Request models
2. **Create API Schemas** - Pydantic models for request/response validation
3. **Implement Auth Routes** - Foundation for all other endpoints
4. **Implement CRUD Routes** - For digests, offers, requests
5. **Add WebSocket Infrastructure** - Manager and endpoints
6. **Build Frontend Components** - Pages and components with Redux
7. **Integrate WebSocket Client** - Real-time updates in frontend
8. **Add Background Workers** - Digest generation and Telegram monitoring
9. **Write Tests** - Unit and integration tests
10. **Deploy & Monitor** - Production readiness

