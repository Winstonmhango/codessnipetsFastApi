import os
import sys
from dotenv import load_dotenv
from sqlalchemy import Column, Integer, JSON

# Load environment variables from .env file
load_dotenv()

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath("."))

try:
    # Import the database engine and User model
    from app.core.database import engine
    from app.models.user import User

    # Add new columns to the User table
    print("Adding gamification fields to User table...")

    # Check if columns already exist
    from sqlalchemy import inspect
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns('users')]

    with engine.begin() as conn:
        from sqlalchemy import text

        # Add total_points column if it doesn't exist
        if 'total_points' not in columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN total_points INTEGER DEFAULT 0"))
            print("Added total_points column")

        # Add level column if it doesn't exist
        if 'level' not in columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN level INTEGER DEFAULT 1"))
            print("Added level column")

        # Add experience column if it doesn't exist
        if 'experience' not in columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN experience INTEGER DEFAULT 0"))
            print("Added experience column")

        # Add streak column if it doesn't exist
        if 'streak' not in columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN streak INTEGER DEFAULT 0"))
            print("Added streak column")

        # Add longest_streak column if it doesn't exist
        if 'longest_streak' not in columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN longest_streak INTEGER DEFAULT 0"))
            print("Added longest_streak column")

        # Add preferences column if it doesn't exist
        if 'preferences' not in columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN preferences JSONB DEFAULT '{}'"))
            print("Added preferences column")

    print("User table updated successfully!")

except Exception as e:
    print(f"Error updating User table: {e}")
