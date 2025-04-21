from sqlalchemy import Boolean, Column, Integer, String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class LearningPath(Base):
    __tablename__ = "learning_paths"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text)
    long_description = Column(Text)
    cover_image = Column(String)
    author = Column(String)
    level = Column(String)
    duration = Column(String)
    tags = Column(JSON)  # Store as JSON array
    article_count = Column(Integer)
    quiz_count = Column(Integer)
    learning_outcomes = Column(JSON)  # Store as JSON array
    prerequisites = Column(JSON)  # Store as JSON array

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now)

    # Relationships
    modules = relationship("LearningPathModule", back_populates="learning_path")
    resources = relationship("LearningPathResource", back_populates="learning_path")


class LearningPathModule(Base):
    __tablename__ = "learning_path_modules"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    estimated_time = Column(String)
    is_completed = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    is_unlocked = Column(Boolean, default=False)
    start_url = Column(String)
    learning_path_id = Column(String, ForeignKey("learning_paths.id"))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now)

    # Relationships
    learning_path = relationship("LearningPath", back_populates="modules")
    content_items = relationship("LearningPathContentItem", back_populates="module")


class LearningPathContentItem(Base):
    __tablename__ = "learning_path_content_items"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    type = Column(String)  # "article", "series", or "booklet"
    is_completed = Column(Boolean, default=False)
    module_id = Column(String, ForeignKey("learning_path_modules.id"))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now)

    # Relationships
    module = relationship("LearningPathModule", back_populates="content_items")


class LearningPathResource(Base):
    __tablename__ = "learning_path_resources"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    type = Column(String)  # "documentation", "github", "video", "article", or "other"
    url = Column(String)
    learning_path_id = Column(String, ForeignKey("learning_paths.id"))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now)

    # Relationships
    learning_path = relationship("LearningPath", back_populates="resources")
