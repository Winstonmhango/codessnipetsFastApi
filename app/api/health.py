from fastapi import APIRouter
from starlette.responses import JSONResponse

router = APIRouter()

@router.get("/health")
def health_check():
    """
    Simple health check endpoint that always returns a 200 status code.
    This is used by Railway to determine if the application is healthy.
    """
    return JSONResponse({
        "status": "healthy",
        "message": "CodeSnippets API is running"
    })
