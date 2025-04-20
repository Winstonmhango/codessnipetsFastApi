from typing import List, Optional
import uuid

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.booklet import Booklet, BookletChapter, BookletUpdate
from app.schemas.booklet import (
    BookletCreate, BookletUpdate as BookletUpdateSchema,
    BookletChapterCreate, BookletChapterUpdate,
    BookletUpdateCreate, BookletUpdateUpdate
)


class CRUDBooklet(CRUDBase[Booklet, BookletCreate, BookletUpdateSchema]):
    def get_by_slug(self, db: Session, *, slug: str) -> Optional[Booklet]:
        return db.query(Booklet).filter(Booklet.slug == slug).first()

    def get_multi_with_details(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Booklet]:
        return db.query(Booklet).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: BookletCreate) -> Booklet:
        # Convert tags, learning_outcomes, and prerequisites to JSON if provided
        tags = obj_in.tags if obj_in.tags else []
        learning_outcomes = obj_in.learning_outcomes if obj_in.learning_outcomes else []
        prerequisites = obj_in.prerequisites if obj_in.prerequisites else []
        
        db_obj = Booklet(
            id=str(uuid.uuid4()),
            title=obj_in.title,
            slug=obj_in.slug,
            description=obj_in.description,
            long_description=obj_in.long_description,
            cover_image=obj_in.cover_image,
            author_id=obj_in.author_id,
            status=obj_in.status,
            estimated_time=obj_in.estimated_time,
            last_updated=obj_in.last_updated,
            tags=tags,
            learning_outcomes=learning_outcomes,
            prerequisites=prerequisites,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


class CRUDBookletChapter(CRUDBase[BookletChapter, BookletChapterCreate, BookletChapterUpdate]):
    def get_multi_by_booklet(
        self, db: Session, *, booklet_id: str, skip: int = 0, limit: int = 100
    ) -> List[BookletChapter]:
        return (
            db.query(BookletChapter)
            .filter(BookletChapter.booklet_id == booklet_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(self, db: Session, *, obj_in: BookletChapterCreate) -> BookletChapter:
        db_obj = BookletChapter(
            id=str(uuid.uuid4()),
            title=obj_in.title,
            slug=obj_in.slug,
            reading_time=obj_in.reading_time,
            is_published=obj_in.is_published,
            publish_date=obj_in.publish_date,
            is_completed=obj_in.is_completed,
            is_premium=obj_in.is_premium,
            is_unlocked=obj_in.is_unlocked,
            is_new=obj_in.is_new,
            booklet_id=obj_in.booklet_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


class CRUDBookletUpdate(CRUDBase[BookletUpdate, BookletUpdateCreate, BookletUpdateUpdate]):
    def get_multi_by_booklet(
        self, db: Session, *, booklet_id: str, skip: int = 0, limit: int = 100
    ) -> List[BookletUpdate]:
        return (
            db.query(BookletUpdate)
            .filter(BookletUpdate.booklet_id == booklet_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(self, db: Session, *, obj_in: BookletUpdateCreate) -> BookletUpdate:
        db_obj = BookletUpdate(
            id=str(uuid.uuid4()),
            title=obj_in.title,
            date=obj_in.date,
            description=obj_in.description,
            chapter_link=obj_in.chapter_link,
            booklet_id=obj_in.booklet_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


booklet = CRUDBooklet(Booklet)
booklet_chapter = CRUDBookletChapter(BookletChapter)
booklet_update = CRUDBookletUpdate(BookletUpdate)
