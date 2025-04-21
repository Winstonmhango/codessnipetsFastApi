import os
import sys
import importlib
import traceback

def test_imports():
    """Test importing key modules"""
    print("=== Testing imports ===")
    modules_to_check = [
        "fastapi", "sqlalchemy", "starlette", "pydantic", 
        "alembic", "psycopg2", "itsdangerous", "uvicorn"
    ]
    
    all_success = True
    for module_name in modules_to_check:
        try:
            module = importlib.import_module(module_name)
            version = getattr(module, "__version__", "unknown")
            print(f"✅ Successfully imported {module_name} (version: {version})")
        except Exception as e:
            all_success = False
            print(f"❌ Failed to import {module_name}: {e}")
            print(traceback.format_exc())
    
    return all_success

def test_app_import():
    """Test importing the FastAPI app"""
    print("\n=== Testing app import ===")
    try:
        from app.main import app
        print(f"✅ Successfully imported app from app.main")
        print(f"App routes:")
        for route in app.routes:
            print(f"  - {route.path} [{', '.join(route.methods)}]")
        return True
    except Exception as e:
        print(f"❌ Failed to import app from app.main: {e}")
        print(traceback.format_exc())
        return False

def test_models_import():
    """Test importing models"""
    print("\n=== Testing models import ===")
    try:
        from app.models import (
            User, Category, Post, Series, Booklet, 
            LearningPath, Quiz, Award, Course, 
            NewsletterSubscription, CoursePrelaunchCampaign
        )
        print("✅ Successfully imported all models")
        return True
    except Exception as e:
        print(f"❌ Failed to import models: {e}")
        print(traceback.format_exc())
        return False

def test_database_connection():
    """Test database connection"""
    print("\n=== Testing database connection ===")
    try:
        from app.core.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).fetchall()
            print(f"✅ Successfully connected to database: {result}")
            return True
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    print("=== App Startup Test ===")
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    
    # Run tests
    imports_ok = test_imports()
    app_ok = test_app_import()
    models_ok = test_models_import()
    db_ok = test_database_connection()
    
    # Summary
    print("\n=== Test Summary ===")
    print(f"Imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"App Import: {'✅ PASS' if app_ok else '❌ FAIL'}")
    print(f"Models Import: {'✅ PASS' if models_ok else '❌ FAIL'}")
    print(f"Database Connection: {'✅ PASS' if db_ok else '❌ FAIL'}")
    
    # Exit with appropriate code
    if imports_ok and app_ok and models_ok and db_ok:
        print("\n✅ All tests passed! The application should start correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. The application may not start correctly.")
        sys.exit(1)
