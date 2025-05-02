from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.db import db
from app.routers import auth, thumbnails, command


# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI application
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Event handlers
@app.on_event("startup")
async def startup_event():
    """Connect to database on startup."""
    await db.connect()


@app.on_event("shutdown")
async def shutdown_event():
    """Disconnect from database on shutdown."""
    await db.disconnect()


# Include routers
app.include_router(auth.router, prefix="/auth")
app.include_router(thumbnails.router)
app.include_router(command.router)


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Check if the API is running."""
    return {"status": "ok"} 