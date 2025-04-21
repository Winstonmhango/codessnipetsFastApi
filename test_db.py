import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables from .env file
load_dotenv()

# Get the database URL from environment variables
database_url = os.environ.get("DATABASE_URL")
print(f"Database URL: {database_url}")

try:
    # Create a SQLAlchemy engine
    engine = create_engine(database_url)
    
    # Try to connect to the database
    with engine.connect() as conn:
        # Execute a simple query
        result = conn.execute(text("SELECT 1"))
        print("Database connection successful!")
        
        # List all tables
        result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
        tables = [row[0] for row in result]
        print(f"Found {len(tables)} tables in the database:")
        for table in tables:
            print(f"- {table}")
            
except Exception as e:
    print(f"Error connecting to database: {e}")
