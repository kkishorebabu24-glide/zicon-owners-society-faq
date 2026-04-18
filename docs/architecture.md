# Architecture Guide

## System Overview

Society App is a community platform built with a modern, scalable architecture designed to handle 3500+ residents' real-time communication needs, AI-powered digest generation, and demand-supply matching.

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React PWA)                      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐   │
│  │  User Dashboard  │  │  Digest Viewer   │  │  Marketplace │   │
│  │  (Responsive)    │  │  (Real-time)     │  │  (Offers/    │   │
│  └──────────────────┘  └──────────────────┘  └──────────────┘   │
│           ↓                    ↓                    ↓             │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │         API Gateway / Authentication Layer                  │ │
│  │  (JWT + OAuth2, CORS, Rate Limiting, Request Validation)   │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                            │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ API Routes Layer                                           │ │
│  │ ├─ /auth/* (login, register, refresh tokens)              │ │
│  │ ├─ /digests/* (get, create, filter)                       │ │
│  │ ├─ /demand-supply/* (offers, requests, matching)          │ │
│  │ └─ /telegram/* (webhook, config)                          │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              ↓                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Business Logic / Service Layer                            │ │
│  │ ├─ AuthService (user management, tokens)                  │ │
│  │ ├─ DigestService (generation, storage)                    │ │
│  │ ├─ AIService (LLM integration, summarization)             │ │
│  │ ├─ MatchingService (supply/demand matching)               │ │
│  │ └─ TelegramService (group monitoring, webhooks)           │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              ↓                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Worker/Queue Layer (Background Tasks)                     │ │
│  │ ├─ DigestGenerator (scheduled daily at 6 AM)              │ │
│  │ ├─ TelegramListener (receive & queue messages)            │ │
│  │ ├─ MessageProcessor (parse, clean, store)                 │ │
│  │ └─ NotificationSender (email, push alerts)                │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
        ↓                       ↓                      ↓
    ┌────────────┐         ┌──────────┐         ┌──────────┐
    │PostgreSQL  │         │  Redis   │         │ Telegram │
    │ Database   │         │(Cache/   │         │   Bot    │
    │            │         │Queue)    │         │  API     │
    └────────────┘         └──────────┘         └──────────┘
        ↓
    ┌─────────────────────────────────────────┐
    │ External Services                       │
    │ ├─ OpenAI/Claude API (Summarization)    │
    │ ├─ Telegram Bot API (Group Monitoring)  │
    │ └─ Email Service (SendGrid/AWS SES)     │
    └─────────────────────────────────────────┘
```

## Core Components

### 1. Frontend (React PWA)

**Technology**: React 18, Redux Toolkit, Material-UI

**Key Features**:
- Progressive Web App (installable, offline support)
- Responsive design (mobile-first)
- Real-time updates (WebSocket/polling)
- Service Worker for caching

**Main Pages**:
- **Dashboard**: User profile, statistics, personalized content
- **Digests**: View, filter, search daily summaries
- **Marketplace**: Browse offers/requests, create new listings
- **Profile**: User settings, preferences, subscriptions

### 2. Backend (FastAPI)

**Technology**: Python 3.10+, FastAPI, SQLAlchemy, Pydantic

**Core Features**:
- RESTful API with OpenAPI/Swagger documentation
- JWT + OAuth2 authentication
- Input validation via Pydantic
- Async request handling
- Dependency injection pattern

**Key Modules**:
- **Auth Module**: User registration, login, token management, role-based access
- **Digest Module**: Create, retrieve, filter, deliver digests
- **Demand-Supply Module**: Manage offers/requests, matching algorithm
- **Telegram Module**: Webhook handling, group configuration
- **AI Module**: LLM integration for summarization

### 3. Database (PostgreSQL)

**Schema Overview**:

```sql
-- Users table
users
├── id (UUID, PK)
├── email (UNIQUE)
├── username
├── password_hash
├── role (admin | moderator | resident)
├── phone
├── created_at
└── updated_at

-- Telegram Groups
telegram_groups
├── id (UUID, PK)
├── group_id (Telegram API ID)
├── name
├── description
├── status (active | inactive)
├── bot_token
├── webhook_secret
├── created_at
└── updated_at

-- Messages (from Telegram)
messages
├── id (UUID, PK)
├── telegram_message_id
├── group_id (FK → telegram_groups)
├── sender_id
├── content
├── created_at (when sent)
└── processed_at

-- Digests
digests
├── id (UUID, PK)
├── group_id (FK → telegram_groups)
├── title
├── summary (AI-generated)
├── original_message_ids (array reference)
├── created_at
├── published_at
└── view_count

-- Offers
offers
├── id (UUID, PK)
├── user_id (FK → users)
├── title
├── description
├── category
├── expiry_date
├── contact_info
├── created_at
└── updated_at

-- Requests
requests
├── id (UUID, PK)
├── user_id (FK → users)
├── title
├── description
├── category
├── budget (optional)
├── created_at
└── updated_at

-- Matches (offer ↔ request)
matches
├── id (UUID, PK)
├── offer_id (FK → offers)
├── request_id (FK → requests)
├── score (0-100, matching algorithm)
├── created_at
└── matched_at
```

### 4. Message Queue & Caching (Redis)

**Purpose**: 
- Task queue for background jobs
- Session caching
- Rate limiting
- Real-time notifications

**Queue Jobs**:
- `digest_generation`: Daily summary creation (6 AM daily)
- `message_processing`: Parse and store Telegram messages
- `matching_algorithm`: Calculate offer/request matches
- `notification_send`: Email/push alerts

### 5. Worker Layer (Background Processors)

**Components**:
- **Telegram Listener**: Maintains connection to Telegram Bot API, receives group messages
- **Message Processor**: Validates, cleans, stores messages
- **Digest Generator**: Runs daily, collects messages, calls AI API, stores result
- **Matching Engine**: Calculates compatibility scores between offers and requests

### 6. External Integrations

#### Telegram Bot API
- **Endpoint**: Receives webhooks for group messages
- **Flow**: Message → Webhook → MessageProcessor → Storage
- **Security**: HMAC validation of webhook

#### OpenAI/Claude API
- **Purpose**: Summarize daily messages into digestible content
- **Prompt Strategy**: 
  - Extractkey topics from messages
  - Generate 3-5 bullet points
  - Highlight action items
- **Caching**: Redis cache for summaries (24-hour TTL)

#### Email Service (SendGrid/AWS SES)
- **Purpose**: Deliver digest emails daily
- **Template**: HTML email with digest, links, personalization
- **Schedule**: Cron job at 7 AM daily

## Data Flow Diagrams

### Telegram Message → Digest Flow

```
1. User sends message in Telegram group
                ↓
2. Telegram Bot API receives message
                ↓
3. Webhook POST to /telegram/webhook
                ↓
4. Validate HMAC signature
                ↓
5. Extract message metadata
   (sender, content, timestamp, group_id)
                ↓
6. Queue message for processing
   (Redis queue: "message_processing")
                ↓
7. Worker picks message from queue
                ↓
8. Clean & parse content
   (remove URLs, emojis, mentions - configurable)
                ↓
9. Check for spam/duplicates
                ↓
10. Store in PostgreSQL
    (messages table)
                ↓
11. [Next day - 6 AM]
    Trigger digest_generation job
                ↓
12. Fetch all messages from past 24 hours
                ↓
13. Call AI API with messages
                ↓
14. Generate summary
                ↓
15. Store digest
                ↓
16. Send email notification (7 AM)
```

### Demand-Supply Matching Flow

```
1. User creates Offer
   POST /demand-supply/offers
                ↓
2. Store offer in DB
                ↓
3. Trigger matching algorithm
   Queue job: "matching_algorithm"
                ↓
4. For each matching Request:
   - Calculate score based on:
     * Category match (exact = 100)
     * Keywords similarity (TF-IDF)
     * User profile compatibility
     * Time recency
                ↓
5. Store matches in DB
   (if score > threshold: 70)
                ↓
6. Notify matching users
   Email: "Found matching offer for your request"
```

## Security Architecture

### Authentication Flow

```
User Login
    ↓
POST /auth/login
    ↓
Verify credentials
    ↓
Generate Access Token (15 min) + Refresh Token (7 days)
    ↓
Return tokens to client
    ↓
Client stores in secure storage (HttpOnly cookie if possible)
    ↓
Subsequent requests include Authorization header
    ↓
Verify JWT signature + exp time
```

### Data Protection

- **Password**: Bcrypt hashing (salt rounds: 12)
- **API Keys**: Encrypted in environment variables, never logged
- **Database**: PostgreSQL encryption at rest (optional)
- **HTTPS**: TLS 1.2+ enforced
- **CORS**: Strict whitelist of allowed origins

### Rate Limiting

- API endpoints: 100 requests per minute per IP
- Authentication: 5 failed attempts → 15-minute lockout
- Telegram webhook: 10 requests per second per group

## Deployment Architecture

### Development
- Local PostgreSQL + Redis
- Docker Compose for reproducibility
- Hot reload enabled

### Staging
- Docker containers
- Managed PostgreSQL (AWS RDS)
- Redis cluster
- GitHub Actions CI/CD

### Production
- Kubernetes cluster (optional)
- Auto-scaling enabled
- CDN for static assets
- Database read replicas
- Regular backups

## Performance Considerations

### Database Optimization
- Indexes on frequently queried columns
- Pagination for list endpoints
- Caching digests (24-hour TTL)

### API Optimization
- Gzip compression
- HTTP caching headers
- GraphQL subset (optional future enhancement)

### Frontend Optimization
- Code splitting per route
- Lazy loading components
- Image optimization
- PWA caching strategy

## Scalability

### Horizontal Scaling
- **Backend**: Multiple FastAPI instances behind load balancer
- **Workers**: Scale worker replicas based on queue depth
- **Database**: Read replicas for read-heavy operations

### Caching Strategy
- Redis for session management
- Browser caching for static assets
- Digest caching (24 hours)

### Monitoring
- Application metrics (requests, errors, latency)
- Database performance (slow queries)
- Worker queue depth
- Error tracking (Sentry)

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PostgreSQL Best Practices](https://wiki.postgresql.org/wiki/Performance_Optimization)
- [Redis Caching Strategies](https://redis.io/topics/patterns)
- [System Design](https://github.com/donnemartin/system-design-primer)
