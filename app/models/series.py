from sqlalchemy import Boolean, Column, Integer, String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Author(Base):
    __tablename__ = "authors"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    avatar = Column(String)
    bio = Column(Text)
    twitter = Column(String)
    github = Column(String)
    linkedin = Column(String)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    series = relationship("Series", back_populates="author_relation")
    booklets = relationship("Booklet", back_populates="author_relation")


class Series(Base):
    __tablename__ = "series"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text)
    long_description = Column(Text)
    cover_image = Column(String)
    author_id = Column(String, ForeignKey("authors.id"))
    level = Column(String)
    estimated_time = Column(String)
    tags = Column(JSON)  # Store as JSON array
    learning_outcomes = Column(JSON)  # Store as JSON array
    prerequisites = Column(JSON)  # Store as JSON array

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    author_relation = relationship("Author", back_populates="series")
    articles = relationship("SeriesArticle", back_populates="series")


class SeriesArticle(Base):
    __tablename__ = "series_articles"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    slug = Column(String, index=True, nullable=False)
    reading_time = Column(Integer)
    is_completed = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    is_unlocked = Column(Boolean, default=False)
    is_new = Column(Boolean, default=False)
    series_id = Column(String, ForeignKey("series.id"))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    series = relationship("Series", back_populates="articles")
