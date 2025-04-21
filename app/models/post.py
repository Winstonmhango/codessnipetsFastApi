from sqlalchemy import Column, String, Text, Integer, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    excerpt = Column(Text)
    content = Column(Text)
    cover_image = Column(String)
    date = Column(DateTime(timezone=True), server_default=func.now())
    author = Column(String, ForeignKey("users.id"))
    category_id = Column(String, ForeignKey("categories.id"))
    reading_time = Column(Integer)

    # Additional fields
    introduction = Column(Text)
    summary = Column(JSON)  # Store as JSON array
    table_of_contents = Column(JSON)  # Store as JSON array
    sections = Column(JSON)  # Store as JSON array
    blocks = Column(JSON)  # Store as JSON array

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    category = relationship("Category", back_populates="posts")
    author_relation = relationship("User")
