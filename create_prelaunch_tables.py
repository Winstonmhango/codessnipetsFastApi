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
        CoursePrelaunchCampaign, PrelaunchSubscriber,
        PrelaunchEmailSequence, PrelaunchEmail
    )
    from app.models.prelaunch import (
        prelaunch_course_association,
        prelaunch_booklet_association,
        prelaunch_series_association
    )

    # Create the new tables
    print("Creating prelaunch tables...")

    # Create Prelaunch tables first
    CoursePrelaunchCampaign.__table__.create(bind=engine, checkfirst=True)
    PrelaunchSubscriber.__table__.create(bind=engine, checkfirst=True)
    PrelaunchEmailSequence.__table__.create(bind=engine, checkfirst=True)
    PrelaunchEmail.__table__.create(bind=engine, checkfirst=True)

    # Create association tables after the main tables
    prelaunch_course_association.create(bind=engine, checkfirst=True)
    prelaunch_booklet_association.create(bind=engine, checkfirst=True)
    prelaunch_series_association.create(bind=engine, checkfirst=True)

    print("Prelaunch tables created successfully!")

except Exception as e:
    print(f"Error creating tables: {e}")
