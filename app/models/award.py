from sqlalchemy import Boolean, Column, Integer, String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text

from app.core.database import Base


class Award(Base):
    __tablename__ = "awards"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    icon = Column(String)  # URL or path to award icon/badge image
    category = Column(String)  # e.g., 'achievement', 'completion', 'special'
    points = Column(Integer, default=0)  # Points awarded for earning this badge
    requirements = Column(JSON)  # JSON object with requirements to earn this award

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=text('NOW()'))
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user_awards = relationship("UserAward", back_populates="award")


class UserAward(Base):
    __tablename__ = "user_awards"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    award_id = Column(String, ForeignKey("awards.id"), nullable=False)
    earned_at = Column(DateTime(timezone=True), server_default=text('NOW()'))
    progress = Column(Integer, default=100)  # Progress percentage (100 means completed)
    award_metadata = Column(JSON)  # Additional data about how the award was earned

    # Relationships
    user = relationship("User", back_populates="awards")
    award = relationship("Award", back_populates="user_awards")
