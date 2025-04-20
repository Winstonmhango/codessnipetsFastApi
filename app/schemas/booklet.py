from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.schemas.series import Author


# Booklet Chapter schemas
class BookletChapterBase(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    reading_time: Optional[int] = None
    is_published: Optional[bool] = False
    publish_date: Optional[str] = None
    is_completed: Optional[bool] = False
    is_premium: Optional[bool] = False
    is_unlocked: Optional[bool] = False
    is_new: Optional[bool] = False


class BookletChapterCreate(BookletChapterBase):
    title: str
    slug: str
    reading_time: int
    booklet_id: str


class BookletChapterUpdate(BookletChapterBase):
    pass


class BookletChapterInDBBase(BookletChapterBase):
    id: str
    booklet_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BookletChapter(BookletChapterInDBBase):
    pass


# Booklet Update schemas
class BookletUpdateBase(BaseModel):
    title: Optional[str] = None
    date: Optional[str] = None
    description: Optional[str] = None
    chapter_link: Optional[str] = None


class BookletUpdateCreate(BookletUpdateBase):
    title: str
    date: str
    description: str
    booklet_id: str


class BookletUpdateUpdate(BookletUpdateBase):
    pass


class BookletUpdateInDBBase(BookletUpdateBase):
    id: str
    booklet_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BookletUpdate(BookletUpdateInDBBase):
    pass


# Booklet schemas
class BookletBase(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    long_description: Optional[str] = None
    cover_image: Optional[str] = None
    status: Optional[str] = None
    estimated_time: Optional[str] = None
    last_updated: Optional[str] = None
    tags: Optional[List[str]] = None
    learning_outcomes: Optional[List[str]] = None
    prerequisites: Optional[List[str]] = None


class BookletCreate(BookletBase):
    title: str
    slug: str
    author_id: str


class BookletUpdate(BookletBase):
    pass


class BookletInDBBase(BookletBase):
    id: str
    author_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Booklet(BookletInDBBase):
    pass


class BookletWithDetails(Booklet):
    author: Author
    chapters: List[BookletChapter]
    updates: List[BookletUpdate]
