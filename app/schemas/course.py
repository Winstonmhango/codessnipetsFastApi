from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel


# Course Category schemas
class CourseCategoryBase(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[str] = None


class CourseCategoryCreate(CourseCategoryBase):
    name: str
    slug: str


class CourseCategoryUpdate(CourseCategoryBase):
    pass


class CourseCategory(CourseCategoryBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CourseCategoryWithSubcategories(CourseCategory):
    subcategories: List["CourseCategoryWithSubcategories"] = []

    class Config:
        from_attributes = True


# Course schemas
class CourseBase(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    subtitle: Optional[str] = None
    description: Optional[str] = None
    long_description: Optional[str] = None
    cover_image: Optional[str] = None
    level: Optional[str] = None
    duration: Optional[str] = None
    price: Optional[float] = 0.0
    is_published: Optional[bool] = False
    is_featured: Optional[bool] = False
    tags: Optional[List[str]] = None
    learning_outcomes: Optional[List[str]] = None
    prerequisites: Optional[List[str]] = None


class CourseCreate(CourseBase):
    title: str
    slug: str
    author_id: str
    category_id: str


class CourseUpdate(CourseBase):
    pass


class Course(CourseBase):
    id: str
    author_id: str
    category_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Course Module schemas
class CourseModuleBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = 0
    is_published: Optional[bool] = False
    is_free_preview: Optional[bool] = False


class CourseModuleCreate(CourseModuleBase):
    title: str
    course_id: str


class CourseModuleUpdate(CourseModuleBase):
    pass


class CourseModule(CourseModuleBase):
    id: str
    course_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Course Topic schemas
class CourseTopicBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = 0
    is_published: Optional[bool] = False


class CourseTopicCreate(CourseTopicBase):
    title: str
    module_id: str


class CourseTopicUpdate(CourseTopicBase):
    pass


class CourseTopic(CourseTopicBase):
    id: str
    module_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Topic Lesson schemas
class TopicLessonBase(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    order: Optional[int] = 0
    lesson_type: Optional[str] = "text"
    media_url: Optional[str] = None
    duration: Optional[int] = None
    is_published: Optional[bool] = False


class TopicLessonCreate(TopicLessonBase):
    title: str
    topic_id: str


class TopicLessonUpdate(TopicLessonBase):
    pass


class TopicLesson(TopicLessonBase):
    id: str
    topic_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Course Enrollment schemas
class CourseEnrollmentBase(BaseModel):
    is_completed: Optional[bool] = False
    progress_percentage: Optional[float] = 0.0


class CourseEnrollmentCreate(CourseEnrollmentBase):
    course_id: str


class CourseEnrollmentUpdate(CourseEnrollmentBase):
    pass


class CourseEnrollment(CourseEnrollmentBase):
    id: str
    user_id: str
    course_id: str
    enrolled_at: datetime
    completed_at: Optional[datetime] = None
    last_accessed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Course Progress schemas
class CourseProgressBase(BaseModel):
    content_type: str  # 'module', 'topic', 'lesson'
    content_id: str
    is_completed: Optional[bool] = False


class CourseProgressCreate(CourseProgressBase):
    enrollment_id: str


class CourseProgressUpdate(CourseProgressBase):
    is_completed: Optional[bool] = None


class CourseProgress(CourseProgressBase):
    id: str
    enrollment_id: str
    completed_at: Optional[datetime] = None
    last_accessed_at: datetime

    class Config:
        from_attributes = True


# Nested schemas for detailed views
class TopicLessonWithQuiz(TopicLesson):
    quiz: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class CourseTopicWithLessons(CourseTopic):
    lessons: List[TopicLessonWithQuiz] = []

    class Config:
        from_attributes = True


class CourseModuleWithTopics(CourseModule):
    topics: List[CourseTopicWithLessons] = []

    class Config:
        from_attributes = True


class CourseWithDetails(Course):
    modules: List[CourseModuleWithTopics] = []
    author: Optional[Dict[str, Any]] = None
    category: Optional[Dict[str, Any]] = None
    enrollment: Optional[CourseEnrollment] = None

    class Config:
        from_attributes = True


# Update circular reference
CourseCategoryWithSubcategories.update_forward_refs()
