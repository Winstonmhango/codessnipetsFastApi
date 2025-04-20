from typing import List, Optional
import uuid

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.learning_path import (
    LearningPath, LearningPathModule, 
    LearningPathContentItem, LearningPathResource
)
from app.schemas.learning_path import (
    LearningPathCreate, LearningPathUpdate,
    LearningPathModuleCreate, LearningPathModuleUpdate,
    LearningPathContentItemCreate, LearningPathContentItemUpdate,
    LearningPathResourceCreate, LearningPathResourceUpdate
)


class CRUDLearningPath(CRUDBase[LearningPath, LearningPathCreate, LearningPathUpdate]):
    def get_by_slug(self, db: Session, *, slug: str) -> Optional[LearningPath]:
        return db.query(LearningPath).filter(LearningPath.slug == slug).first()

    def get_multi_with_details(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[LearningPath]:
        return db.query(LearningPath).offset(skip).limit(limit).all()

    def get_featured(self, db: Session, *, limit: int = 3) -> List[LearningPath]:
        return db.query(LearningPath).limit(limit).all()

    def get_by_tag(
        self, db: Session, *, tag: str, skip: int = 0, limit: int = 100
    ) -> List[LearningPath]:
        # This is a simplified approach since we're storing tags as JSON
        # In a real-world scenario, you might want to use a more efficient query
        paths = db.query(LearningPath).all()
        result = []
        for path in paths:
            if path.tags and tag in path.tags:
                result.append(path)
        return result[skip:skip+limit]

    def get_related(
        self, db: Session, *, current_id: str, limit: int = 3
    ) -> List[LearningPath]:
        return (
            db.query(LearningPath)
            .filter(LearningPath.id != current_id)
            .limit(limit)
            .all()
        )

    def create(self, db: Session, *, obj_in: LearningPathCreate) -> LearningPath:
        # Convert tags, learning_outcomes, and prerequisites to JSON if provided
        tags = obj_in.tags if obj_in.tags else []
        learning_outcomes = obj_in.learning_outcomes if obj_in.learning_outcomes else []
        prerequisites = obj_in.prerequisites if obj_in.prerequisites else []
        
        db_obj = LearningPath(
            id=str(uuid.uuid4()),
            title=obj_in.title,
            slug=obj_in.slug,
            description=obj_in.description,
            long_description=obj_in.long_description,
            cover_image=obj_in.cover_image,
            author=obj_in.author,
            level=obj_in.level,
            duration=obj_in.duration,
            tags=tags,
            article_count=obj_in.article_count,
            quiz_count=obj_in.quiz_count,
            learning_outcomes=learning_outcomes,
            prerequisites=prerequisites,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


class CRUDLearningPathModule(CRUDBase[LearningPathModule, LearningPathModuleCreate, LearningPathModuleUpdate]):
    def get_multi_by_learning_path(
        self, db: Session, *, learning_path_id: str, skip: int = 0, limit: int = 100
    ) -> List[LearningPathModule]:
        return (
            db.query(LearningPathModule)
            .filter(LearningPathModule.learning_path_id == learning_path_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(self, db: Session, *, obj_in: LearningPathModuleCreate) -> LearningPathModule:
        db_obj = LearningPathModule(
            id=str(uuid.uuid4()),
            title=obj_in.title,
            description=obj_in.description,
            estimated_time=obj_in.estimated_time,
            is_completed=obj_in.is_completed,
            is_premium=obj_in.is_premium,
            is_unlocked=obj_in.is_unlocked,
            start_url=obj_in.start_url,
            learning_path_id=obj_in.learning_path_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


class CRUDLearningPathContentItem(CRUDBase[LearningPathContentItem, LearningPathContentItemCreate, LearningPathContentItemUpdate]):
    def get_multi_by_module(
        self, db: Session, *, module_id: str, skip: int = 0, limit: int = 100
    ) -> List[LearningPathContentItem]:
        return (
            db.query(LearningPathContentItem)
            .filter(LearningPathContentItem.module_id == module_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(self, db: Session, *, obj_in: LearningPathContentItemCreate) -> LearningPathContentItem:
        db_obj = LearningPathContentItem(
            id=str(uuid.uuid4()),
            title=obj_in.title,
            type=obj_in.type,
            is_completed=obj_in.is_completed,
            module_id=obj_in.module_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


class CRUDLearningPathResource(CRUDBase[LearningPathResource, LearningPathResourceCreate, LearningPathResourceUpdate]):
    def get_multi_by_learning_path(
        self, db: Session, *, learning_path_id: str, skip: int = 0, limit: int = 100
    ) -> List[LearningPathResource]:
        return (
            db.query(LearningPathResource)
            .filter(LearningPathResource.learning_path_id == learning_path_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(self, db: Session, *, obj_in: LearningPathResourceCreate) -> LearningPathResource:
        db_obj = LearningPathResource(
            id=str(uuid.uuid4()),
            title=obj_in.title,
            description=obj_in.description,
            type=obj_in.type,
            url=obj_in.url,
            learning_path_id=obj_in.learning_path_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


learning_path = CRUDLearningPath(LearningPath)
learning_path_module = CRUDLearningPathModule(LearningPathModule)
learning_path_content_item = CRUDLearningPathContentItem(LearningPathContentItem)
learning_path_resource = CRUDLearningPathResource(LearningPathResource)
