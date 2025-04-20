from typing import List, Optional

from pydantic import BaseModel


# Shared properties
class CategoryBase(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None


# Properties to receive via API on creation
class CategoryCreate(CategoryBase):
    name: str
    slug: str


# Properties to receive via API on update
class CategoryUpdate(CategoryBase):
    pass


# Properties shared by models stored in DB
class CategoryInDBBase(CategoryBase):
    id: str

    class Config:
        from_attributes = True


# Properties to return via API
class Category(CategoryInDBBase):
    pass


# Additional properties to return via API
class CategoryWithPostCount(Category):
    post_count: int
