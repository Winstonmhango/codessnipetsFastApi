import os
from typing import Dict, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app
from app.models.user import User
from app.core.security import get_password_hash


# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db() -> Generator:
    # Create the database and tables
    Base.metadata.create_all(bind=engine)
    
    # Create a new session for each test
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        
    # Drop the database after the test
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db) -> Generator:
    # Override the get_db dependency to use the test database
    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as c:
        yield c
    
    # Reset the dependency override
    app.dependency_overrides = {}


@pytest.fixture(scope="function")
def superuser_token_headers(client: TestClient, db) -> Dict[str, str]:
    """
    Return a valid token for the superuser
    """
    # Create a superuser in the database
    superuser = User(
        id="00000000-0000-0000-0000-000000000000",
        email="admin@example.com",
        username="admin",
        first_name="Admin",
        last_name="User",
        hashed_password=get_password_hash("admin"),
        is_active=True,
        is_superuser=True,
    )
    db.add(superuser)
    db.commit()
    
    # Get a token for the superuser
    login_data = {
        "username": "admin@example.com",
        "password": "admin",
    }
    r = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers


@pytest.fixture(scope="function")
def normal_user_token_headers(client: TestClient, db) -> Dict[str, str]:
    """
    Return a valid token for a normal user
    """
    # Create a normal user in the database
    user = User(
        id="11111111-1111-1111-1111-111111111111",
        email="user@example.com",
        username="user",
        first_name="Normal",
        last_name="User",
        hashed_password=get_password_hash("password"),
        is_active=True,
        is_superuser=False,
    )
    db.add(user)
    db.commit()
    
    # Get a token for the user
    login_data = {
        "username": "user@example.com",
        "password": "password",
    }
    r = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers
