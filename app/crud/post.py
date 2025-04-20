from typing import List, Optional
import uuid

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.post import Post
from app.schemas.post import PostCreate, PostUpdate


class CRUDPost(CRUDBase[Post, PostCreate, PostUpdate]):
    def get_by_slug(self, db: Session, *, slug: str) -> Optional[Post]:
        return db.query(Post).filter(Post.slug == slug).first()

    def get_multi_by_category(
        self, db: Session, *, category_id: str, skip: int = 0, limit: int = 100
    ) -> List[Post]:
        return (
            db.query(Post)
            .filter(Post.category_id == category_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_multi_by_author(
        self, db: Session, *, author: str, skip: int = 0, limit: int = 100
    ) -> List[Post]:
        return (
            db.query(Post)
            .filter(Post.author == author)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_related_posts(
        self, db: Session, *, current_slug: str, category_id: str, limit: int = 2
    ) -> List[Post]:
        return (
            db.query(Post)
            .filter(Post.slug != current_slug, Post.category_id == category_id)
            .limit(limit)
            .all()
        )

    def create(self, db: Session, *, obj_in: PostCreate) -> Post:
        # Convert summary, table_of_contents, sections, and blocks to JSON if provided
        summary = obj_in.summary if obj_in.summary else []
        table_of_contents = obj_in.table_of_contents if obj_in.table_of_contents else []
        sections = obj_in.sections if obj_in.sections else []
        blocks = obj_in.blocks if obj_in.blocks else []
        
        db_obj = Post(
            id=str(uuid.uuid4()),
            title=obj_in.title,
            slug=obj_in.slug,
            excerpt=obj_in.excerpt,
            content=obj_in.content,
            cover_image=obj_in.cover_image,
            author=obj_in.author,
            category_id=obj_in.category,
            reading_time=obj_in.reading_time,
            introduction=obj_in.introduction,
            summary=summary,
            table_of_contents=table_of_contents,
            sections=sections,
            blocks=blocks,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


post = CRUDPost(Post)
