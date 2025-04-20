from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import JSONResponse
import logging
from contextlib import asynccontextmanager

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import engine, Base

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    try:
        # Log startup information
        logging.info("Starting up the application")
        logging.info(f"Database URL: {settings.DATABASE_URL}")

        # Test database connection
        with engine.connect() as _:
            logging.info("Database connection successful")
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        raise e

    yield

    # Shutdown logic
    logging.info("Shutting down the application")

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
    return JSONResponse({
        "status": "healthy",
        "message": "CodeSnippets API is running",
        "version": "1.0.0",
        "environment": "production"
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
