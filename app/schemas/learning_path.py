from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


# Learning Path Content Item schemas
class LearningPathContentItemBase(BaseModel):
    title: Optional[str] = None
    type: Optional[str] = None  # "article", "series", or "booklet"
    is_completed: Optional[bool] = False


class LearningPathContentItemCreate(LearningPathContentItemBase):
    title: str
    type: str
    module_id: str


class LearningPathContentItemUpdate(LearningPathContentItemBase):
    pass


class LearningPathContentItemInDBBase(LearningPathContentItemBase):
    id: str
    module_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LearningPathContentItem(LearningPathContentItemInDBBase):
    pass


# Learning Path Module schemas
class LearningPathModuleBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    estimated_time: Optional[str] = None
    is_completed: Optional[bool] = False
    is_premium: Optional[bool] = False
    is_unlocked: Optional[bool] = False
    start_url: Optional[str] = None


class LearningPathModuleCreate(LearningPathModuleBase):
    title: str
    estimated_time: str
    start_url: str
    learning_path_id: str


class LearningPathModuleUpdate(LearningPathModuleBase):
    pass


class LearningPathModuleInDBBase(LearningPathModuleBase):
    id: str
    learning_path_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LearningPathModule(LearningPathModuleInDBBase):
    pass


class LearningPathModuleWithItems(LearningPathModule):
    content_items: List[LearningPathContentItem]


# Learning Path Resource schemas
class LearningPathResourceBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None  # "documentation", "github", "video", "article", or "other"
    url: Optional[str] = None


class LearningPathResourceCreate(LearningPathResourceBase):
    title: str
    description: str
    type: str
    url: str
    learning_path_id: str


class LearningPathResourceUpdate(LearningPathResourceBase):
    pass


class LearningPathResourceInDBBase(LearningPathResourceBase):
    id: str
    learning_path_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LearningPathResource(LearningPathResourceInDBBase):
    pass


# Learning Path schemas
class LearningPathBase(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    long_description: Optional[str] = None
    cover_image: Optional[str] = None
    author: Optional[str] = None
    level: Optional[str] = None
    duration: Optional[str] = None
    tags: Optional[List[str]] = None
    article_count: Optional[int] = None
    quiz_count: Optional[int] = None
    learning_outcomes: Optional[List[str]] = None
    prerequisites: Optional[List[str]] = None


class LearningPathCreate(LearningPathBase):
    title: str
    slug: str
    author: str


class LearningPathUpdate(LearningPathBase):
    pass


class LearningPathInDBBase(LearningPathBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LearningPath(LearningPathInDBBase):
    pass


class LearningPathWithDetails(LearningPath):
    modules: List[LearningPathModuleWithItems]
    resources: List[LearningPathResource]
