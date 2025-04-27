from sqlalchemy import Boolean, Column, String, DateTime, Integer, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    # Gamification fields
    total_points = Column(Integer, default=0)  # Total points earned
    level = Column(Integer, default=1)  # User level
    experience = Column(Integer, default=0)  # Experience points
    streak = Column(Integer, default=0)  # Current streak (days)
    longest_streak = Column(Integer, default=0)  # Longest streak achieved
    preferences = Column(JSON)  # User preferences as JSON

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=text('NOW()'))
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    quiz_attempts = relationship("UserQuizAttempt", back_populates="user")
    awards = relationship("UserAward", back_populates="user")
