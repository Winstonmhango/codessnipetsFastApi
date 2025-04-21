from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import JSONResponse
import logging
import os
import sys
import datetime
from contextlib import asynccontextmanager

from app.api.v1.api import api_router
from app.api.health import router as health_router
from app.core.config import settings
from app.core.database import engine, Base, get_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info("===== Starting up the application =====")
    logger.info(f"Environment: {os.environ.get('ENVIRONMENT', 'development')}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Current directory: {os.getcwd()}")

    # Log configuration
    logger.info(f"API Version: {settings.API_V1_STR}")
    logger.info(f"Project Name: {settings.PROJECT_NAME}")

    # Log environment variables (sanitized)
    for key, value in os.environ.items():
        if not any(sensitive in key.lower() for sensitive in ["secret", "password", "key", "token"]):
            logger.info(f"ENV: {key}={value}")

    # Check if database check is disabled
    if os.environ.get("DISABLE_DATABASE_CHECK_ON_STARTUP") == "true":
        logger.info("Database connection check on startup is disabled")
    else:
        # Attempt to connect to the database, but don't fail startup if it fails
        try:
            # Parse the URL to display info without credentials
            from urllib.parse import urlparse
            parsed = urlparse(str(settings.DATABASE_URL))
            safe_url = f'{parsed.scheme}://{parsed.hostname}:{parsed.port}{parsed.path}'

            logger.info(f"Attempting to connect to database: {safe_url}")

            # Try to connect with a timeout
            import time
            start_time = time.time()
            with engine.connect() as conn:
                from sqlalchemy import text
                result = conn.execute(text("SELECT 1"))
                elapsed = time.time() - start_time
                logger.info(f"Database connection successful (took {elapsed:.2f}s)")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            logger.warning("Application will start, but database operations may fail")

    logger.info("Application startup complete")
    yield

    # Shutdown logic
    logger.info("===== Shutting down the application =====")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.API_V1_STR.startswith('/') else f"/{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Add session middleware
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR if settings.API_V1_STR.startswith('/') else f"/{settings.API_V1_STR}")

# Include health check router at root level
app.include_router(health_router)

# Add debug routes
@app.get("/debug/environment")
def debug_environment():
    """Debug endpoint to show environment variables (sanitized)"""
    env_vars = {}
    for key, value in os.environ.items():
        # Skip sensitive variables
        if any(sensitive in key.lower() for sensitive in ["secret", "password", "key", "token"]):
            env_vars[key] = "[REDACTED]"
        else:
            env_vars[key] = value
    return {"environment": env_vars}

@app.get("/debug/config")
def debug_config():
    """Debug endpoint to show application configuration"""
    config_dict = {}
    for key in dir(settings):
        if not key.startswith("_") and not callable(getattr(settings, key)):
            value = getattr(settings, key)
            # Skip sensitive values
            if any(sensitive in key.lower() for sensitive in ["secret", "password", "key", "token"]):
                config_dict[key] = "[REDACTED]"
            else:
                config_dict[key] = str(value)
    return {"config": config_dict}

@app.get("/")
def root():
    """Root endpoint for the API."""
    return JSONResponse({
        "message": "Welcome to CodeSnippets API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    })

# Health check endpoint moved to app/api/health.py

if __name__ == "__main__":
    import uvicorn
    import os
    # Get PORT from environment or use the default from settings
    port_str = os.getenv("PORT")
    port = int(port_str) if port_str else settings.PORT
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )
