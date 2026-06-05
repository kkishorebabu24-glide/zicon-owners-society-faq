"""
Society App - FastAPI Backend
Main application entry point
"""

import asyncio
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.config import settings
from app.core.websocket_manager import init_connection_manager, close_connection_manager, get_connection_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle app startup and shutdown events"""
    # Startup
    logger.info("Starting Society App...")
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
        logger.error(f"Startup error: {e}")
        raise
    
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
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    manager = get_connection_manager()
    stats = manager.get_connection_stats()
    return {
        "status": "ok",
        "version": "0.1.0",
        "websocket_connections": stats,
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

