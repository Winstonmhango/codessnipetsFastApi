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
        Quiz, QuizQuestion, QuizAnswer, UserQuizAttempt,
        Award, UserAward
    )
    
    # Create the new tables
    print("Creating gamification tables...")
    
    # Create Quiz tables
    Quiz.__table__.create(bind=engine, checkfirst=True)
    QuizQuestion.__table__.create(bind=engine, checkfirst=True)
    QuizAnswer.__table__.create(bind=engine, checkfirst=True)
    UserQuizAttempt.__table__.create(bind=engine, checkfirst=True)
    
    # Create Award tables
    Award.__table__.create(bind=engine, checkfirst=True)
    UserAward.__table__.create(bind=engine, checkfirst=True)
    
    print("Gamification tables created successfully!")
    
except Exception as e:
    print(f"Error creating tables: {e}")
