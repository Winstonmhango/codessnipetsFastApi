import os
import sys
import platform
import datetime
import traceback
import importlib
import logging
from fastapi import APIRouter
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/debug/system")
def debug_system():
    """
    Debug endpoint to show system information.
    """
    # Collect system information
    system_info = {
        "python_version": sys.version,
        "platform": platform.platform(),
        "current_directory": os.getcwd(),
        "timestamp": datetime.datetime.now().isoformat(),
        "python_path": sys.path,
    }
    
    return JSONResponse({"system": system_info})

@router.get("/debug/modules")
def debug_modules():
    """
    Debug endpoint to check if important modules can be imported.
    """
    # Try to import important modules
    modules_to_check = [
        "fastapi", "sqlalchemy", "starlette", "pydantic", 
        "alembic", "psycopg2", "itsdangerous", "uvicorn"
    ]
    
    import_checks = {}
    for module_name in modules_to_check:
        try:
            module = importlib.import_module(module_name)
            import_checks[module_name] = {
                "status": "success",
                "version": getattr(module, "__version__", "unknown")
            }
        except Exception as e:
            import_checks[module_name] = {
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    
    return JSONResponse({"modules": import_checks})

@router.get("/debug/files")
def debug_files():
    """
    Debug endpoint to check if important files exist.
    """
    # Check if important files exist
    files_to_check = [
        "app/main.py",
        "app/api/v1/api.py",
        "app/core/database.py",
        "app/core/config.py",
        "app/models/__init__.py",
        "app/models/user.py",
        "app/models/post.py",
        "app/models/award.py",
        "app/models/course.py",
        "app/models/learning_path.py",
        "app/models/quiz.py",
        "app/models/series.py",
        "app/models/marketing.py",
        "app/models/prelaunch.py",
        "app/models/booklet.py",
        "app/models/category.py",
    ]
    
    file_checks = {}
    for file_path in files_to_check:
        file_checks[file_path] = {
            "exists": os.path.exists(file_path),
            "size": os.path.getsize(file_path) if os.path.exists(file_path) else None,
            "is_file": os.path.isfile(file_path) if os.path.exists(file_path) else None,
        }
    
    return JSONResponse({"files": file_checks})

@router.get("/debug/database")
def debug_database():
    """
    Debug endpoint to check database connection.
    """
    # Try a database connection
    db_info = {
        "status": "not_checked",
        "error": None,
        "traceback": None,
        "database_url_type": None,
    }
    
    try:
        # Get database URL type
        from app.core.config import settings
        db_info["database_url_type"] = str(settings.DATABASE_URL).split(":")[0] if settings.DATABASE_URL else "None"
        
        # Try to connect
        from app.core.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            db_info["status"] = "connected"
            db_info["result"] = str(result.fetchall())
    except Exception as e:
        db_info["status"] = "error"
        db_info["error"] = str(e)
        db_info["traceback"] = traceback.format_exc()
        logger.error(f"Debug database connection failed: {e}\n{db_info['traceback']}")
    
    return JSONResponse({"database": db_info})

@router.get("/debug/models")
def debug_models():
    """
    Debug endpoint to check if models can be imported.
    """
    # Try to import models
    models_to_check = [
        "User", "Category", "Post", "Series", "Booklet", 
        "LearningPath", "Quiz", "Award", "Course", 
        "NewsletterSubscription", "CoursePrelaunchCampaign"
    ]
    
    model_checks = {}
    try:
        from app.models import __init__
        model_checks["__init__"] = {
            "status": "success",
            "imported_models": dir(__init__)
        }
    except Exception as e:
        model_checks["__init__"] = {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }
    
    for model_name in models_to_check:
        try:
            # Try to dynamically import the model
            from app.models import __init__
            model = getattr(__init__, model_name, None)
            
            if model:
                model_checks[model_name] = {
                    "status": "success",
                    "attributes": [attr for attr in dir(model) if not attr.startswith("_")]
                }
            else:
                model_checks[model_name] = {
                    "status": "not_found",
                    "error": f"Model {model_name} not found in app.models"
                }
        except Exception as e:
            model_checks[model_name] = {
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    
    return JSONResponse({"models": model_checks})

@router.get("/debug/all")
def debug_all():
    """
    Debug endpoint to run all checks.
    """
    system = debug_system()
    modules = debug_modules()
    files = debug_files()
    database = debug_database()
    models = debug_models()
    
    return JSONResponse({
        "system": system.body,
        "modules": modules.body,
        "files": files.body,
        "database": database.body,
        "models": models.body,
        "timestamp": datetime.datetime.now().isoformat()
    })
