import os
import sys

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath("."))

# Run alembic command
os.system("alembic revision --autogenerate -m \"Initial migration\"")
