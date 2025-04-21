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
        NewsletterSubscription, MarketingBanner
    )
    
    # Create the new tables
    print("Creating marketing tables...")
    
    # Create Marketing tables
    NewsletterSubscription.__table__.create(bind=engine, checkfirst=True)
    MarketingBanner.__table__.create(bind=engine, checkfirst=True)
    
    print("Marketing tables created successfully!")
    
except Exception as e:
    print(f"Error creating tables: {e}")
