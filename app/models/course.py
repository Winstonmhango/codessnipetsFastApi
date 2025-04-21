from sqlalchemy import Boolean, Column, Integer, String, Text, ForeignKey, DateTime, JSON, Float, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

# Association table for courses and learning paths
course_learning_path = Table(
    "course_learning_path",
    Base.metadata,
    Column("course_id", String, ForeignKey("courses.id"), primary_key=True),
    Column("learning_path_id", String, ForeignKey("learning_paths.id"), primary_key=True)
)


class CourseCategory(Base):
    __tablename__ = "course_categories"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text)
    parent_id = Column(String, ForeignKey("course_categories.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    courses = relationship("Course", back_populates="category")
    subcategories = relationship("CourseCategory", 
                                backref="parent", 
                                remote_side=[id],
                                cascade="all, delete-orphan")


class Course(Base):
    __tablename__ = "courses"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    subtitle = Column(String)
    description = Column(Text)
    long_description = Column(Text)
    cover_image = Column(String)
    author_id = Column(String, ForeignKey("authors.id"))
    category_id = Column(String, ForeignKey("course_categories.id"))
    level = Column(String)  # 'beginner', 'intermediate', 'advanced'
    duration = Column(String)  # Estimated duration
    price = Column(Float, default=0.0)  # 0 for free courses
    is_published = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    tags = Column(JSON)  # Store as JSON array
    learning_outcomes = Column(JSON)  # Store as JSON array
    prerequisites = Column(JSON)  # Store as JSON array
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True))
    
    # Relationships
    author = relationship("Author", back_populates="courses")
    category = relationship("CourseCategory", back_populates="courses")
    modules = relationship("CourseModule", back_populates="course", cascade="all, delete-orphan")
    enrollments = relationship("CourseEnrollment", back_populates="course", cascade="all, delete-orphan")
    learning_paths = relationship("LearningPath", 
                                secondary=course_learning_path,
                                backref="courses")


class CourseModule(Base):
    __tablename__ = "course_modules"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    course_id = Column(String, ForeignKey("courses.id"), nullable=False)
    order = Column(Integer, default=0)  # For ordering modules
    is_published = Column(Boolean, default=False)
    is_free_preview = Column(Boolean, default=False)  # Free preview for paid courses
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    course = relationship("Course", back_populates="modules")
    topics = relationship("CourseTopic", back_populates="module", cascade="all, delete-orphan")


class CourseTopic(Base):
    __tablename__ = "course_topics"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    module_id = Column(String, ForeignKey("course_modules.id"), nullable=False)
    order = Column(Integer, default=0)  # For ordering topics
    is_published = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    module = relationship("CourseModule", back_populates="topics")
    lessons = relationship("TopicLesson", back_populates="topic", cascade="all, delete-orphan")


class TopicLesson(Base):
    __tablename__ = "topic_lessons"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text)
    topic_id = Column(String, ForeignKey("course_topics.id"), nullable=False)
    order = Column(Integer, default=0)  # For ordering lessons
    lesson_type = Column(String, default="text")  # 'text', 'video', 'audio', 'interactive'
    media_url = Column(String)  # URL for video/audio content
    duration = Column(Integer)  # Duration in seconds
    is_published = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    topic = relationship("CourseTopic", back_populates="lessons")
    quiz = relationship("Quiz", 
                      primaryjoin="and_(TopicLesson.id==Quiz.content_id, "
                                 "Quiz.content_type=='lesson')",
                      backref="lesson",
                      uselist=False,
                      viewonly=True)


class CourseEnrollment(Base):
    __tablename__ = "course_enrollments"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    course_id = Column(String, ForeignKey("courses.id"), nullable=False)
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True))
    progress_percentage = Column(Float, default=0.0)
    last_accessed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", backref="course_enrollments")
    course = relationship("Course", back_populates="enrollments")
    progress_records = relationship("CourseProgress", back_populates="enrollment", cascade="all, delete-orphan")


class CourseProgress(Base):
    __tablename__ = "course_progress"

    id = Column(String, primary_key=True, index=True)
    enrollment_id = Column(String, ForeignKey("course_enrollments.id"), nullable=False)
    content_type = Column(String, nullable=False)  # 'module', 'topic', 'lesson'
    content_id = Column(String, nullable=False)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True))
    last_accessed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    enrollment = relationship("CourseEnrollment", back_populates="progress_records")
