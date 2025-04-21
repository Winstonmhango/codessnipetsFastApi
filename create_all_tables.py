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
    
    # Import all models to ensure they're registered with SQLAlchemy
    from app.models.user import User
    from app.models.category import Category
    from app.models.post import Post
    from app.models.series import Author, Series, SeriesArticle
    from app.models.booklet import Booklet, BookletChapter, BookletUpdate
    from app.models.learning_path import (
        LearningPath, LearningPathModule, LearningPathContentItem, LearningPathResource
    )
    from app.models.quiz import Quiz, QuizQuestion, QuizAnswer, UserQuizAttempt
    from app.models.award import Award, UserAward
    from app.models.course import (
        CourseCategory, Course, CourseModule, CourseTopic, 
        TopicLesson, CourseEnrollment, CourseProgress
    )
    from app.models.marketing import NewsletterSubscription, MarketingBanner
    from app.models.prelaunch import (
        CoursePrelaunchCampaign, PrelaunchSubscriber, 
        PrelaunchEmailSequence, PrelaunchEmail,
        prelaunch_course_association,
        prelaunch_booklet_association,
        prelaunch_series_association
    )
    
    # Create all tables
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("All tables created successfully!")
    
except Exception as e:
    print(f"Error creating tables: {e}")
    # Continue execution even if there's an error
    print("Continuing anyway...")
