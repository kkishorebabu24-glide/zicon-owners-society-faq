"""
Society App - FastAPI Backend
Main application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from .config import settings

# Create FastAPI app
app = FastAPI(
    title="Society App API",
    description="Community platform for residential societies",
    version="0.1.0",
    docs_url="/docs" if not settings.ENVIRONMENT == "production" else None,
    redoc_url="/redoc" if not settings.ENVIRONMENT == "production" else None,
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
    return {"status": "ok", "version": "0.1.0"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Society App API",
        "docs": "/docs",
        "version": "0.1.0",
    }


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# TODO: Add route includes
# from app.api.routes import auth, digests, demand_supply, telegram
# app.include_router(auth.router)
# app.include_router(digests.router)
# app.include_router(demand_supply.router)
# app.include_router(telegram.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
