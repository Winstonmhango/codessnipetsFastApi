from typing import List, Optional
import uuid

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


class CRUDCategory(CRUDBase[Category, CategoryCreate, CategoryUpdate]):
    def get_by_slug(self, db: Session, *, slug: str) -> Optional[Category]:
        return db.query(Category).filter(Category.slug == slug).first()

    def get_multi_with_post_count(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[dict]:
        categories = db.query(Category).offset(skip).limit(limit).all()
        result = []
        for category in categories:
            post_count = len(category.posts)
            category_dict = {
                "id": category.id,
                "name": category.name,
                "slug": category.slug,
                "description": category.description,
                "post_count": post_count
            }
            result.append(category_dict)
        return result

    def create(self, db: Session, *, obj_in: CategoryCreate) -> Category:
        db_obj = Category(
            id=str(uuid.uuid4()),
            name=obj_in.name,
            slug=obj_in.slug,
            description=obj_in.description,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


category = CRUDCategory(Category)
