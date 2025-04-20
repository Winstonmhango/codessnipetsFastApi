from typing import List, Optional
import uuid

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.series import Author, Series, SeriesArticle
from app.schemas.series import (
    AuthorCreate, AuthorUpdate,
    SeriesCreate, SeriesUpdate,
    SeriesArticleCreate, SeriesArticleUpdate
)


class CRUDAuthor(CRUDBase[Author, AuthorCreate, AuthorUpdate]):
    def create(self, db: Session, *, obj_in: AuthorCreate) -> Author:
        db_obj = Author(
            id=str(uuid.uuid4()),
            name=obj_in.name,
            avatar=obj_in.avatar,
            bio=obj_in.bio,
            twitter=obj_in.twitter,
            github=obj_in.github,
            linkedin=obj_in.linkedin,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


class CRUDSeries(CRUDBase[Series, SeriesCreate, SeriesUpdate]):
    def get_by_slug(self, db: Session, *, slug: str) -> Optional[Series]:
        return db.query(Series).filter(Series.slug == slug).first()

    def get_multi_with_details(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Series]:
        return db.query(Series).offset(skip).limit(limit).all()

    def get_related_series(
        self, db: Session, *, current_id: str, limit: int = 3
    ) -> List[Series]:
        # Get the current series to find its tags
        current_series = self.get(db, id=current_id)
        if not current_series or not current_series.tags:
            return db.query(Series).filter(Series.id != current_id).limit(limit).all()
        
        # Find series with similar tags
        return (
            db.query(Series)
            .filter(Series.id != current_id)
            .limit(limit)
            .all()
        )

    def create(self, db: Session, *, obj_in: SeriesCreate) -> Series:
        # Convert tags, learning_outcomes, and prerequisites to JSON if provided
        tags = obj_in.tags if obj_in.tags else []
        learning_outcomes = obj_in.learning_outcomes if obj_in.learning_outcomes else []
        prerequisites = obj_in.prerequisites if obj_in.prerequisites else []
        
        db_obj = Series(
            id=str(uuid.uuid4()),
            title=obj_in.title,
            slug=obj_in.slug,
            description=obj_in.description,
            long_description=obj_in.long_description,
            cover_image=obj_in.cover_image,
            author_id=obj_in.author_id,
            level=obj_in.level,
            estimated_time=obj_in.estimated_time,
            tags=tags,
            learning_outcomes=learning_outcomes,
            prerequisites=prerequisites,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


class CRUDSeriesArticle(CRUDBase[SeriesArticle, SeriesArticleCreate, SeriesArticleUpdate]):
    def get_multi_by_series(
        self, db: Session, *, series_id: str, skip: int = 0, limit: int = 100
    ) -> List[SeriesArticle]:
        return (
            db.query(SeriesArticle)
            .filter(SeriesArticle.series_id == series_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(self, db: Session, *, obj_in: SeriesArticleCreate) -> SeriesArticle:
        db_obj = SeriesArticle(
            id=str(uuid.uuid4()),
            title=obj_in.title,
            slug=obj_in.slug,
            reading_time=obj_in.reading_time,
            is_completed=obj_in.is_completed,
            is_premium=obj_in.is_premium,
            is_unlocked=obj_in.is_unlocked,
            is_new=obj_in.is_new,
            series_id=obj_in.series_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


author = CRUDAuthor(Author)
series = CRUDSeries(Series)
series_article = CRUDSeriesArticle(SeriesArticle)
