import os
import sys
from dotenv import load_dotenv
from sqlalchemy import inspect

# Load environment variables from .env file
load_dotenv()

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath("."))

try:
    # Import the database engine
    from app.core.database import engine
    
    # Create an inspector
    inspector = inspect(engine)
    
    # Get table names
    tables = inspector.get_table_names()
    
    print(f"Found {len(tables)} tables in the database:")
    for table in tables:
        print(f"- {table}")
        
        # Get columns for each table
        columns = inspector.get_columns(table)
        print(f"  Columns: {len(columns)}")
        for column in columns[:3]:  # Show only first 3 columns to keep output manageable
            print(f"    - {column['name']} ({column['type']})")
        if len(columns) > 3:
            print(f"    - ... and {len(columns) - 3} more columns")
        print()
    
except Exception as e:
    print(f"Error listing tables: {e}")
