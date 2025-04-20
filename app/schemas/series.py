from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


# Author schemas
class AuthorBase(BaseModel):
    name: Optional[str] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None
    twitter: Optional[str] = None
    github: Optional[str] = None
    linkedin: Optional[str] = None


class AuthorCreate(AuthorBase):
    name: str


class AuthorUpdate(AuthorBase):
    pass


class AuthorInDBBase(AuthorBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Author(AuthorInDBBase):
    pass


# Series Article schemas
class SeriesArticleBase(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    reading_time: Optional[int] = None
    is_completed: Optional[bool] = False
    is_premium: Optional[bool] = False
    is_unlocked: Optional[bool] = False
    is_new: Optional[bool] = False


class SeriesArticleCreate(SeriesArticleBase):
    title: str
    slug: str
    reading_time: int
    series_id: str


class SeriesArticleUpdate(SeriesArticleBase):
    pass


class SeriesArticleInDBBase(SeriesArticleBase):
    id: str
    series_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SeriesArticle(SeriesArticleInDBBase):
    pass


# Series schemas
class SeriesBase(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    long_description: Optional[str] = None
    cover_image: Optional[str] = None
    level: Optional[str] = None
    estimated_time: Optional[str] = None
    tags: Optional[List[str]] = None
    learning_outcomes: Optional[List[str]] = None
    prerequisites: Optional[List[str]] = None


class SeriesCreate(SeriesBase):
    title: str
    slug: str
    author_id: str


class SeriesUpdate(SeriesBase):
    pass


class SeriesInDBBase(SeriesBase):
    id: str
    author_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Series(SeriesInDBBase):
    pass


class SeriesWithDetails(Series):
    author: Author
    articles: List[SeriesArticle]
