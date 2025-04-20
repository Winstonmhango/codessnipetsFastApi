import pytest
from sqlalchemy.orm import Session

from app import crud
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import verify_password


def test_create_user(db: Session) -> None:
    email = "test@example.com"
    username = "testuser"
    password = "password"
    user_in = UserCreate(email=email, username=username, password=password)
    user = crud.user.create(db, obj_in=user_in)
    assert user.email == email
    assert user.username == username
    assert hasattr(user, "hashed_password")
    assert verify_password(password, user.hashed_password)


def test_authenticate_user(db: Session) -> None:
    email = "test-auth@example.com"
    username = "test-auth"
    password = "password"
    user_in = UserCreate(email=email, username=username, password=password)
    user = crud.user.create(db, obj_in=user_in)
    authenticated_user = crud.user.authenticate(db, email=email, password=password)
    assert authenticated_user
    assert user.email == authenticated_user.email


def test_not_authenticate_user(db: Session) -> None:
    email = "test-auth2@example.com"
    username = "test-auth2"
    password = "password"
    user_in = UserCreate(email=email, username=username, password=password)
    crud.user.create(db, obj_in=user_in)
    authenticated_user = crud.user.authenticate(db, email=email, password="wrong-password")
    assert authenticated_user is None


def test_get_user(db: Session) -> None:
    email = "test-get@example.com"
    username = "test-get"
    password = "password"
    user_in = UserCreate(email=email, username=username, password=password)
    user = crud.user.create(db, obj_in=user_in)
    user_2 = crud.user.get(db, id=user.id)
    assert user_2
    assert user.email == user_2.email
    assert user.username == user_2.username
    assert user.id == user_2.id


def test_update_user(db: Session) -> None:
    email = "test-update@example.com"
    username = "test-update"
    password = "password"
    user_in = UserCreate(email=email, username=username, password=password)
    user = crud.user.create(db, obj_in=user_in)
    new_password = "new-password"
    user_in_update = UserUpdate(password=new_password)
    crud.user.update(db, db_obj=user, obj_in=user_in_update)
    user_2 = crud.user.get(db, id=user.id)
    assert user_2
    assert user.email == user_2.email
    assert verify_password(new_password, user_2.hashed_password)
