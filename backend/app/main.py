"""
Society App - FastAPI Backend
Main application entry point
"""

import asyncio
import logging
import os
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.config import settings
from app.core.database import SessionLocal, init_db
from app.core.jwt_handler import hash_password
from app.core.websocket_manager import init_connection_manager, close_connection_manager, get_connection_manager
from app.db.models import User, UserRole

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_demo_user():
    """Create a local demo account for testing if it does not already exist."""
    demo_email = os.getenv("DEMO_EMAIL", "demo@societyapp.com")
    demo_password = os.getenv("DEMO_PASSWORD", "DemoPass123!")

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == demo_email).first()
        if existing:
            logger.info("Demo user already exists")
            return existing

        demo_user = User(
            first_name="Demo",
            last_name="User",
            email=demo_email,
            phone="9999999999",
            password_hash=hash_password(demo_password),
            bio="Seeded demo account for local testing",
            address="Local development",
            role=UserRole.RESIDENT,
            is_active=True,
            email_verified=True,
            phone_verified=True,
        )
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)
        logger.info("Created demo user: %s", demo_email)
        return demo_user
    except Exception as exc:
        db.rollback()
        logger.warning("Demo user seeding skipped: %s", exc)
        return None
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle app startup and shutdown events"""
    # Startup
    logger.info("Starting Society App...")
    try:
        init_db()
        logger.info("Database tables initialized")
        seed_demo_user()
    except Exception as e:
        logger.warning(f"Database initialization skipped: {e}")

    try:
        await init_connection_manager(settings.REDIS_URL)
        logger.info("WebSocket manager initialized")

        # Start Redis pub/sub subscriptions
        manager = get_connection_manager()
        asyncio.create_task(manager.subscribe_to_redis("listing_updates"))
        asyncio.create_task(manager.subscribe_to_redis("digest_delivery"))
        asyncio.create_task(manager.subscribe_to_redis("marketplace"))
        logger.info("Redis pub/sub subscriptions started")
    except Exception as e:
        logger.warning(f"Redis/WebSocket startup skipped: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Society App...")
    try:
        await close_connection_manager()
        logger.info("WebSocket manager closed")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")


# Create FastAPI app with lifespan
app = FastAPI(
    title="Society App API",
    description="Community platform for residential societies",
    version="0.1.0",
    docs_url="/docs" if not settings.ENVIRONMENT == "production" else None,
    redoc_url="/redoc" if not settings.ENVIRONMENT == "production" else None,
    lifespan=lifespan,
)

# Add middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)


@app.api_route("/health", methods=["GET", "HEAD"])
async def health_check(request: Request):
    """Health check endpoint"""
    if request.method == "HEAD":
        return Response(status_code=200)
    try:
        manager = get_connection_manager()
        stats = manager.get_connection_stats()
        return {
            "status": "ok",
            "version": "0.1.0",
            "websocket_connections": stats,
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "degraded",
            "version": "0.1.0",
            "error": str(e)
        }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Society App API",
        "docs": "/docs",
        "version": "0.1.0",
        "websocket_url": "ws://localhost:8000/api/v1/marketplace/ws/listings",
    }


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# Import and register routers
try:
    from app.api.routes import demand_supply, digests, auth, notifications, telegram
    
    app.include_router(demand_supply.router)
    app.include_router(digests.router)
    app.include_router(auth.router)
    app.include_router(notifications.router)
    app.include_router(telegram.router)
    
    logger.info("All routers registered successfully")
except ImportError as e:
    logger.warning(f"Failed to import routers: {e}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
