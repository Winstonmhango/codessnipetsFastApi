from typing import List, Optional, Dict, Any, Union
import uuid
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from app.crud.base import CRUDBase
from app.models.course import (
    CourseCategory, Course, CourseModule, CourseTopic, 
    TopicLesson, CourseEnrollment, CourseProgress
)
from app.schemas.course import (
    CourseCategoryCreate, CourseCategoryUpdate,
    CourseCreate, CourseUpdate,
    CourseModuleCreate, CourseModuleUpdate,
    CourseTopicCreate, CourseTopicUpdate,
    TopicLessonCreate, TopicLessonUpdate,
    CourseEnrollmentCreate, CourseEnrollmentUpdate,
    CourseProgressCreate, CourseProgressUpdate
)


class CRUDCourseCategory(CRUDBase[CourseCategory, CourseCategoryCreate, CourseCategoryUpdate]):
    def get_by_slug(self, db: Session, *, slug: str) -> Optional[CourseCategory]:
        return db.query(CourseCategory).filter(CourseCategory.slug == slug).first()
    
    def get_root_categories(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[CourseCategory]:
        return db.query(CourseCategory).filter(CourseCategory.parent_id.is_(None)).offset(skip).limit(limit).all()
    
    def get_subcategories(self, db: Session, *, parent_id: str) -> List[CourseCategory]:
        return db.query(CourseCategory).filter(CourseCategory.parent_id == parent_id).all()
    
    def create(self, db: Session, *, obj_in: CourseCategoryCreate) -> CourseCategory:
        db_obj = CourseCategory(
            id=str(uuid.uuid4()),
            name=obj_in.name,
            slug=obj_in.slug,
            description=obj_in.description,
            parent_id=obj_in.parent_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


class CRUDCourse(CRUDBase[Course, CourseCreate, CourseUpdate]):
    def get_by_slug(self, db: Session, *, slug: str) -> Optional[Course]:
        return db.query(Course).filter(Course.slug == slug).first()
    
    def get_by_category(self, db: Session, *, category_id: str, skip: int = 0, limit: int = 100) -> List[Course]:
        return db.query(Course).filter(Course.category_id == category_id).offset(skip).limit(limit).all()
    
    def get_by_author(self, db: Session, *, author_id: str, skip: int = 0, limit: int = 100) -> List[Course]:
        return db.query(Course).filter(Course.author_id == author_id).offset(skip).limit(limit).all()
    
    def get_featured(self, db: Session, *, limit: int = 6) -> List[Course]:
        return db.query(Course).filter(
            and_(Course.is_published == True, Course.is_featured == True)
        ).limit(limit).all()
    
    def get_latest(self, db: Session, *, limit: int = 10) -> List[Course]:
        return db.query(Course).filter(
            Course.is_published == True
        ).order_by(desc(Course.published_at)).limit(limit).all()
    
    def search(self, db: Session, *, query: str, skip: int = 0, limit: int = 100) -> List[Course]:
        search_query = f"%{query}%"
        return db.query(Course).filter(
            and_(
                Course.is_published == True,
                or_(
                    Course.title.ilike(search_query),
                    Course.description.ilike(search_query),
                    Course.long_description.ilike(search_query)
                )
            )
        ).offset(skip).limit(limit).all()
    
    def create(self, db: Session, *, obj_in: CourseCreate) -> Course:
        # Convert tags, learning_outcomes, and prerequisites to JSON if provided
        tags = obj_in.tags if obj_in.tags else []
        learning_outcomes = obj_in.learning_outcomes if obj_in.learning_outcomes else []
        prerequisites = obj_in.prerequisites if obj_in.prerequisites else []
        
        db_obj = Course(
            id=str(uuid.uuid4()),
            title=obj_in.title,
            slug=obj_in.slug,
            subtitle=obj_in.subtitle,
            description=obj_in.description,
            long_description=obj_in.long_description,
            cover_image=obj_in.cover_image,
            author_id=obj_in.author_id,
            category_id=obj_in.category_id,
            level=obj_in.level,
            duration=obj_in.duration,
            price=obj_in.price,
            is_published=obj_in.is_published,
            is_featured=obj_in.is_featured,
            tags=tags,
            learning_outcomes=learning_outcomes,
            prerequisites=prerequisites,
            published_at=datetime.now() if obj_in.is_published else None
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def publish(self, db: Session, *, db_obj: Course) -> Course:
        db_obj.is_published = True
        db_obj.published_at = datetime.now()
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def unpublish(self, db: Session, *, db_obj: Course) -> Course:
        db_obj.is_published = False
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def add_to_learning_path(self, db: Session, *, course_id: str, learning_path_id: str) -> Course:
        from app.models.learning_path import LearningPath
        
        course = self.get(db, id=course_id)
        learning_path = db.query(LearningPath).filter(LearningPath.id == learning_path_id).first()
        
        if course and learning_path:
            course.learning_paths.append(learning_path)
            db.commit()
            db.refresh(course)
        
        return course
    
    def remove_from_learning_path(self, db: Session, *, course_id: str, learning_path_id: str) -> Course:
        from app.models.learning_path import LearningPath
        
        course = self.get(db, id=course_id)
        learning_path = db.query(LearningPath).filter(LearningPath.id == learning_path_id).first()
        
        if course and learning_path and learning_path in course.learning_paths:
            course.learning_paths.remove(learning_path)
            db.commit()
            db.refresh(course)
        
        return course


class CRUDCourseModule(CRUDBase[CourseModule, CourseModuleCreate, CourseModuleUpdate]):
    def get_by_course(self, db: Session, *, course_id: str) -> List[CourseModule]:
        return db.query(CourseModule).filter(CourseModule.course_id == course_id).order_by(CourseModule.order).all()
    
    def create(self, db: Session, *, obj_in: CourseModuleCreate) -> CourseModule:
        # Get the highest order value for this course
        highest_order = db.query(CourseModule).filter(
            CourseModule.course_id == obj_in.course_id
        ).order_by(desc(CourseModule.order)).first()
        
        order = 0
        if highest_order:
            order = highest_order.order + 1
        
        db_obj = CourseModule(
            id=str(uuid.uuid4()),
            title=obj_in.title,
            description=obj_in.description,
            course_id=obj_in.course_id,
            order=order,
            is_published=obj_in.is_published,
            is_free_preview=obj_in.is_free_preview
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def reorder(self, db: Session, *, module_id: str, new_order: int) -> CourseModule:
        module = self.get(db, id=module_id)
        if not module:
            return None
        
        # Get all modules for this course
        modules = self.get_by_course(db, course_id=module.course_id)
        
        # Update orders
        current_order = module.order
        if new_order > current_order:
            # Moving down
            for m in modules:
                if current_order < m.order <= new_order:
                    m.order -= 1
                    db.add(m)
        else:
            # Moving up
            for m in modules:
                if new_order <= m.order < current_order:
                    m.order += 1
                    db.add(m)
        
        # Update the module's order
        module.order = new_order
        db.add(module)
        db.commit()
        db.refresh(module)
        return module


class CRUDCourseTopic(CRUDBase[CourseTopic, CourseTopicCreate, CourseTopicUpdate]):
    def get_by_module(self, db: Session, *, module_id: str) -> List[CourseTopic]:
        return db.query(CourseTopic).filter(CourseTopic.module_id == module_id).order_by(CourseTopic.order).all()
    
    def create(self, db: Session, *, obj_in: CourseTopicCreate) -> CourseTopic:
        # Get the highest order value for this module
        highest_order = db.query(CourseTopic).filter(
            CourseTopic.module_id == obj_in.module_id
        ).order_by(desc(CourseTopic.order)).first()
        
        order = 0
        if highest_order:
            order = highest_order.order + 1
        
        db_obj = CourseTopic(
            id=str(uuid.uuid4()),
            title=obj_in.title,
            description=obj_in.description,
            module_id=obj_in.module_id,
            order=order,
            is_published=obj_in.is_published
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def reorder(self, db: Session, *, topic_id: str, new_order: int) -> CourseTopic:
        topic = self.get(db, id=topic_id)
        if not topic:
            return None
        
        # Get all topics for this module
        topics = self.get_by_module(db, module_id=topic.module_id)
        
        # Update orders
        current_order = topic.order
        if new_order > current_order:
            # Moving down
            for t in topics:
                if current_order < t.order <= new_order:
                    t.order -= 1
                    db.add(t)
        else:
            # Moving up
            for t in topics:
                if new_order <= t.order < current_order:
                    t.order += 1
                    db.add(t)
        
        # Update the topic's order
        topic.order = new_order
        db.add(topic)
        db.commit()
        db.refresh(topic)
        return topic


class CRUDTopicLesson(CRUDBase[TopicLesson, TopicLessonCreate, TopicLessonUpdate]):
    def get_by_topic(self, db: Session, *, topic_id: str) -> List[TopicLesson]:
        return db.query(TopicLesson).filter(TopicLesson.topic_id == topic_id).order_by(TopicLesson.order).all()
    
    def create(self, db: Session, *, obj_in: TopicLessonCreate) -> TopicLesson:
        # Get the highest order value for this topic
        highest_order = db.query(TopicLesson).filter(
            TopicLesson.topic_id == obj_in.topic_id
        ).order_by(desc(TopicLesson.order)).first()
        
        order = 0
        if highest_order:
            order = highest_order.order + 1
        
        db_obj = TopicLesson(
            id=str(uuid.uuid4()),
            title=obj_in.title,
            content=obj_in.content,
            topic_id=obj_in.topic_id,
            order=order,
            lesson_type=obj_in.lesson_type,
            media_url=obj_in.media_url,
            duration=obj_in.duration,
            is_published=obj_in.is_published
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def reorder(self, db: Session, *, lesson_id: str, new_order: int) -> TopicLesson:
        lesson = self.get(db, id=lesson_id)
        if not lesson:
            return None
        
        # Get all lessons for this topic
        lessons = self.get_by_topic(db, topic_id=lesson.topic_id)
        
        # Update orders
        current_order = lesson.order
        if new_order > current_order:
            # Moving down
            for l in lessons:
                if current_order < l.order <= new_order:
                    l.order -= 1
                    db.add(l)
        else:
            # Moving up
            for l in lessons:
                if new_order <= l.order < current_order:
                    l.order += 1
                    db.add(l)
        
        # Update the lesson's order
        lesson.order = new_order
        db.add(lesson)
        db.commit()
        db.refresh(lesson)
        return lesson
    
    def create_quiz(self, db: Session, *, lesson_id: str, quiz_data: Dict[str, Any]) -> Dict[str, Any]:
        from app.crud.quiz import quiz as quiz_crud
        from app.schemas.quiz import QuizCreate
        
        lesson = self.get(db, id=lesson_id)
        if not lesson:
            return None
        
        # Create quiz schema
        quiz_in = QuizCreate(
            title=quiz_data.get("title", f"Quiz for {lesson.title}"),
            description=quiz_data.get("description", ""),
            content_type="lesson",
            content_id=lesson_id,
            passing_score=quiz_data.get("passing_score", 70.0),
            time_limit=quiz_data.get("time_limit"),
            randomize_questions=quiz_data.get("randomize_questions", False),
            show_correct_answers=quiz_data.get("show_correct_answers", True),
            questions=quiz_data.get("questions", [])
        )
        
        # Create quiz
        quiz = quiz_crud.create_with_questions(db, obj_in=quiz_in)
        return quiz


class CRUDCourseEnrollment(CRUDBase[CourseEnrollment, CourseEnrollmentCreate, CourseEnrollmentUpdate]):
    def get_by_user_and_course(self, db: Session, *, user_id: str, course_id: str) -> Optional[CourseEnrollment]:
        return db.query(CourseEnrollment).filter(
            and_(
                CourseEnrollment.user_id == user_id,
                CourseEnrollment.course_id == course_id
            )
        ).first()
    
    def get_by_user(self, db: Session, *, user_id: str, skip: int = 0, limit: int = 100) -> List[CourseEnrollment]:
        return db.query(CourseEnrollment).filter(
            CourseEnrollment.user_id == user_id
        ).offset(skip).limit(limit).all()
    
    def create_with_user(self, db: Session, *, obj_in: CourseEnrollmentCreate, user_id: str) -> CourseEnrollment:
        # Check if enrollment already exists
        existing = self.get_by_user_and_course(db, user_id=user_id, course_id=obj_in.course_id)
        if existing:
            return existing
        
        db_obj = CourseEnrollment(
            id=str(uuid.uuid4()),
            user_id=user_id,
            course_id=obj_in.course_id,
            is_completed=obj_in.is_completed,
            progress_percentage=obj_in.progress_percentage,
            last_accessed_at=datetime.now()
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def mark_completed(self, db: Session, *, enrollment_id: str) -> CourseEnrollment:
        enrollment = self.get(db, id=enrollment_id)
        if enrollment:
            enrollment.is_completed = True
            enrollment.completed_at = datetime.now()
            enrollment.progress_percentage = 100.0
            db.add(enrollment)
            db.commit()
            db.refresh(enrollment)
        return enrollment
    
    def update_progress(self, db: Session, *, enrollment_id: str, progress_percentage: float) -> CourseEnrollment:
        enrollment = self.get(db, id=enrollment_id)
        if enrollment:
            enrollment.progress_percentage = progress_percentage
            enrollment.last_accessed_at = datetime.now()
            if progress_percentage >= 100.0:
                enrollment.is_completed = True
                enrollment.completed_at = datetime.now()
            db.add(enrollment)
            db.commit()
            db.refresh(enrollment)
        return enrollment


class CRUDCourseProgress(CRUDBase[CourseProgress, CourseProgressCreate, CourseProgressUpdate]):
    def get_by_enrollment_and_content(
        self, db: Session, *, enrollment_id: str, content_type: str, content_id: str
    ) -> Optional[CourseProgress]:
        return db.query(CourseProgress).filter(
            and_(
                CourseProgress.enrollment_id == enrollment_id,
                CourseProgress.content_type == content_type,
                CourseProgress.content_id == content_id
            )
        ).first()
    
    def get_by_enrollment(self, db: Session, *, enrollment_id: str) -> List[CourseProgress]:
        return db.query(CourseProgress).filter(CourseProgress.enrollment_id == enrollment_id).all()
    
    def create_or_update(
        self, db: Session, *, enrollment_id: str, content_type: str, content_id: str, is_completed: bool = False
    ) -> CourseProgress:
        # Check if progress record already exists
        progress = self.get_by_enrollment_and_content(
            db, enrollment_id=enrollment_id, content_type=content_type, content_id=content_id
        )
        
        if progress:
            # Update existing record
            progress.is_completed = is_completed
            if is_completed and not progress.completed_at:
                progress.completed_at = datetime.now()
            progress.last_accessed_at = datetime.now()
        else:
            # Create new record
            progress = CourseProgress(
                id=str(uuid.uuid4()),
                enrollment_id=enrollment_id,
                content_type=content_type,
                content_id=content_id,
                is_completed=is_completed,
                completed_at=datetime.now() if is_completed else None,
                last_accessed_at=datetime.now()
            )
        
        db.add(progress)
        db.commit()
        db.refresh(progress)
        
        # Update enrollment progress
        self.update_enrollment_progress(db, enrollment_id=enrollment_id)
        
        return progress
    
    def update_enrollment_progress(self, db: Session, *, enrollment_id: str) -> None:
        from app.models.course import CourseEnrollment, CourseModule, CourseTopic, TopicLesson
        
        # Get enrollment
        enrollment = db.query(CourseEnrollment).filter(CourseEnrollment.id == enrollment_id).first()
        if not enrollment:
            return
        
        # Get course structure
        course = db.query(Course).filter(Course.id == enrollment.course_id).first()
        if not course:
            return
        
        modules = db.query(CourseModule).filter(CourseModule.course_id == course.id).all()
        if not modules:
            return
        
        # Count total and completed items
        total_items = 0
        completed_items = 0
        
        for module in modules:
            topics = db.query(CourseTopic).filter(CourseTopic.module_id == module.id).all()
            for topic in topics:
                lessons = db.query(TopicLesson).filter(TopicLesson.topic_id == topic.id).all()
                total_items += len(lessons)
                
                for lesson in lessons:
                    progress = self.get_by_enrollment_and_content(
                        db, enrollment_id=enrollment_id, content_type="lesson", content_id=lesson.id
                    )
                    if progress and progress.is_completed:
                        completed_items += 1
        
        # Calculate progress percentage
        if total_items > 0:
            progress_percentage = (completed_items / total_items) * 100
        else:
            progress_percentage = 0
        
        # Update enrollment
        enrollment.progress_percentage = progress_percentage
        enrollment.last_accessed_at = datetime.now()
        if progress_percentage >= 100:
            enrollment.is_completed = True
            enrollment.completed_at = datetime.now()
        
        db.add(enrollment)
        db.commit()


course_category = CRUDCourseCategory(CourseCategory)
course = CRUDCourse(Course)
course_module = CRUDCourseModule(CourseModule)
course_topic = CRUDCourseTopic(CourseTopic)
topic_lesson = CRUDTopicLesson(TopicLesson)
course_enrollment = CRUDCourseEnrollment(CourseEnrollment)
course_progress = CRUDCourseProgress(CourseProgress)
