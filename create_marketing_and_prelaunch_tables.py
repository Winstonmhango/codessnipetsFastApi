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
    
    # Import the models
    from app.models.marketing import NewsletterSubscription, MarketingBanner
    from app.models.prelaunch import (
        CoursePrelaunchCampaign, PrelaunchSubscriber, 
        PrelaunchEmailSequence, PrelaunchEmail,
        prelaunch_course_association,
        prelaunch_booklet_association,
        prelaunch_series_association
    )
    
    # Create the tables
    print("Creating marketing and prelaunch tables...")
    
    # Create marketing tables
    print("Creating marketing tables...")
    NewsletterSubscription.__table__.create(bind=engine, checkfirst=True)
    MarketingBanner.__table__.create(bind=engine, checkfirst=True)
    
    # Create prelaunch tables
    print("Creating prelaunch tables...")
    CoursePrelaunchCampaign.__table__.create(bind=engine, checkfirst=True)
    PrelaunchSubscriber.__table__.create(bind=engine, checkfirst=True)
    PrelaunchEmailSequence.__table__.create(bind=engine, checkfirst=True)
    PrelaunchEmail.__table__.create(bind=engine, checkfirst=True)
    
    # Create association tables
    print("Creating association tables...")
    prelaunch_course_association.create(bind=engine, checkfirst=True)
    prelaunch_booklet_association.create(bind=engine, checkfirst=True)
    prelaunch_series_association.create(bind=engine, checkfirst=True)
    
    print("All tables created successfully!")
    
except Exception as e:
    print(f"Error creating tables: {e}")
    # Continue execution even if there's an error
    print("Continuing anyway...")
