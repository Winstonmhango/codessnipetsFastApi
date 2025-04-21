from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel


# Award Schemas
class AwardBase(BaseModel):
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    category: Optional[str] = None
    points: int = 0
    requirements: Dict[str, Any] = {}


class AwardCreate(AwardBase):
    pass


class AwardUpdate(AwardBase):
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    category: Optional[str] = None
    points: Optional[int] = None
    requirements: Optional[Dict[str, Any]] = None


class Award(AwardBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# User Award Schemas
class UserAwardBase(BaseModel):
    award_id: str
    progress: int = 100
    award_metadata: Dict[str, Any] = {}


class UserAwardCreate(UserAwardBase):
    pass


class UserAwardUpdate(UserAwardBase):
    award_id: Optional[str] = None
    progress: Optional[int] = None
    award_metadata: Optional[Dict[str, Any]] = None


class UserAward(UserAwardBase):
    id: str
    user_id: str
    earned_at: datetime

    class Config:
        from_attributes = True


# Award with details
class AwardWithDetails(Award):
    user_count: int = 0

    class Config:
        from_attributes = True


# User with Awards
class UserWithAwards(BaseModel):
    id: str
    username: str
    awards: List[UserAward] = []

    class Config:
        from_attributes = True
