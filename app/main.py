from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import JSONResponse
import logging
import os
from contextlib import asynccontextmanager

from app.api.v1.api import api_router
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
    logger.info("Starting up the application")
    logger.info(f"Environment: {os.environ.get('ENVIRONMENT', 'development')}")

    # Log configuration
    logger.info(f"API Version: {settings.API_V1_STR}")
    logger.info(f"Project Name: {settings.PROJECT_NAME}")

    # Attempt to connect to the database, but don't fail startup if it fails
    try:
        logger.info(f"Attempting to connect to database: {settings.DATABASE_URL}")
        with engine.connect() as conn:
            logger.info("Database connection successful")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        logger.warning("Application will start, but database operations may fail")

    yield

    # Shutdown logic
    logger.info("Shutting down the application")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
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
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    """Root endpoint that serves as a health check for the API."""
    try:
        # Simple database connection check, but don't fail if it doesn't work
        db_status = "connected"
        try:
            with engine.connect() as _:
                pass
        except Exception as e:
            logger.warning(f"Health check database connection failed: {e}")
            db_status = "disconnected"

        return JSONResponse({
            "status": "healthy",
            "message": "CodeSnippets API is running",
            "version": "1.0.0",
            "environment": os.environ.get("ENVIRONMENT", "production"),
            "database": db_status
        })
    except Exception as e:
        logger.error(f"Error in health check endpoint: {e}")
        # Always return a 200 response for the health check
        return JSONResponse({
            "status": "degraded",
            "message": "CodeSnippets API is running with issues",
            "error": str(e)
        })

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
