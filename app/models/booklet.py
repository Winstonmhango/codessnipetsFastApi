from sqlalchemy import Boolean, Column, Integer, String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Booklet(Base):
    __tablename__ = "booklets"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text)
    long_description = Column(Text)
    cover_image = Column(String)
    author_id = Column(String, ForeignKey("authors.id"))
    status = Column(String)
    estimated_time = Column(String)
    last_updated = Column(String)
    tags = Column(JSON)  # Store as JSON array
    learning_outcomes = Column(JSON)  # Store as JSON array
    prerequisites = Column(JSON)  # Store as JSON array

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now)

    # Relationships
    author_relation = relationship("Author", back_populates="booklets")
    chapters = relationship("BookletChapter", back_populates="booklet")
    updates = relationship("BookletUpdate", back_populates="booklet")


class BookletChapter(Base):
    __tablename__ = "booklet_chapters"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    slug = Column(String, index=True, nullable=False)
    reading_time = Column(Integer)
    is_published = Column(Boolean, default=False)
    publish_date = Column(String)
    is_completed = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    is_unlocked = Column(Boolean, default=False)
    is_new = Column(Boolean, default=False)
    booklet_id = Column(String, ForeignKey("booklets.id"))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now)

    # Relationships
    booklet = relationship("Booklet", back_populates="chapters")


class BookletUpdate(Base):
    __tablename__ = "booklet_updates"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    date = Column(String)
    description = Column(Text)
    chapter_link = Column(String)
    booklet_id = Column(String, ForeignKey("booklets.id"))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now)

    # Relationships
    booklet = relationship("Booklet", back_populates="updates")
