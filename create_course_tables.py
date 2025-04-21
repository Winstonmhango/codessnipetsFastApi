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
        CourseCategory, Course, CourseModule, CourseTopic, 
        TopicLesson, CourseEnrollment, CourseProgress
    )
    
    # Create the new tables
    print("Creating course tables...")
    
    # Create Course tables
    CourseCategory.__table__.create(bind=engine, checkfirst=True)
    Course.__table__.create(bind=engine, checkfirst=True)
    CourseModule.__table__.create(bind=engine, checkfirst=True)
    CourseTopic.__table__.create(bind=engine, checkfirst=True)
    TopicLesson.__table__.create(bind=engine, checkfirst=True)
    CourseEnrollment.__table__.create(bind=engine, checkfirst=True)
    CourseProgress.__table__.create(bind=engine, checkfirst=True)
    
    # Create association table for courses and learning paths
    from app.models.course import course_learning_path
    course_learning_path.create(bind=engine, checkfirst=True)
    
    print("Course tables created successfully!")
    
except Exception as e:
    print(f"Error creating tables: {e}")
