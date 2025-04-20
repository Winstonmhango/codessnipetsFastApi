from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field


# Table of Contents Item
class TableOfContentsItem(BaseModel):
    id: str
    title: str
    level: int


# Blog Section
class BlogSection(BaseModel):
    id: str
    title: str
    level: int
    content: str
    subsections: Optional[List["BlogSection"]] = None


# Block Editor Types
class EditorBlock(BaseModel):
    id: str
    type: str
    content: str
    data: Optional[Dict[str, Any]] = None


# Shared properties
class PostBase(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    excerpt: Optional[str] = None
    content: Optional[str] = None
    cover_image: Optional[str] = None
    author: Optional[str] = None
    category: Optional[str] = None
    reading_time: Optional[int] = None
    introduction: Optional[str] = None
    summary: Optional[List[str]] = None
    table_of_contents: Optional[List[TableOfContentsItem]] = None
    sections: Optional[List[BlogSection]] = None
    blocks: Optional[List[EditorBlock]] = None


# Properties to receive via API on creation
class PostCreate(PostBase):
    title: str
    slug: str
    content: str
    category: str
    author: str


# Properties to receive via API on update
class PostUpdate(PostBase):
    pass


# Properties shared by models stored in DB
class PostInDBBase(PostBase):
    id: str
    date: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Properties to return via API
class Post(PostInDBBase):
    pass


# Properties to return for a list of posts
class PostList(BaseModel):
    id: str
    title: str
    slug: str
    excerpt: str
    cover_image: str
    date: datetime
    author: str
    category: str
    reading_time: int

    class Config:
        from_attributes = True
