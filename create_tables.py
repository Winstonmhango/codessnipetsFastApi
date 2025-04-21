import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath("."))

try:
    # Import the database models and engine
    from app.core.database import Base, engine
    from app.models import (
        User, Category, Post, 
        Author, Series, SeriesArticle,
        Booklet, BookletChapter, BookletUpdate,
        LearningPath, LearningPathModule, LearningPathContentItem, LearningPathResource
    )
    
    # Create all tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")
    
except Exception as e:
    print(f"Error creating tables: {e}")
