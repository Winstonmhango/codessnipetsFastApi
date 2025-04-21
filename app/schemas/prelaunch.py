from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, HttpUrl


# CoursePrelaunchCampaign Schemas
class CoursePrelaunchCampaignBase(BaseModel):
    title: str
    slug: str
    description: Optional[str] = None
    
    # Campaign details
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = True
    
    # Lead magnet details
    lead_magnet_title: Optional[str] = None
    lead_magnet_description: Optional[str] = None
    lead_magnet_file_url: Optional[str] = None
    
    # Landing page content
    header_image_url: Optional[str] = None
    content: Optional[str] = None
    cta_text: Optional[str] = None
    cta_url: Optional[str] = None
    
    # Pricing and enrollment details
    early_bird_price: Optional[int] = None
    regular_price: Optional[int] = None
    max_enrollments: Optional[int] = None


class CoursePrelaunchCampaignCreate(CoursePrelaunchCampaignBase):
    pass


class CoursePrelaunchCampaignUpdate(CoursePrelaunchCampaignBase):
    title: Optional[str] = None
    slug: Optional[str] = None


class CoursePrelaunchCampaign(CoursePrelaunchCampaignBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    
    # Campaign statistics
    view_count: int
    signup_count: int
    conversion_rate: int
    
    class Config:
        from_attributes = True


class CoursePrelaunchCampaignWithRelations(CoursePrelaunchCampaign):
    courses: Optional[List[Dict[str, Any]]] = []
    booklets: Optional[List[Dict[str, Any]]] = []
    series: Optional[List[Dict[str, Any]]] = []
    subscribers_count: Optional[int] = 0
    email_sequences: Optional[List[Dict[str, Any]]] = []


# PrelaunchSubscriber Schemas
class PrelaunchSubscriberBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    campaign_id: str
    
    # Tracking
    source: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None
    
    # Custom fields
    custom_fields: Optional[Dict[str, Any]] = None


class PrelaunchSubscriberCreate(PrelaunchSubscriberBase):
    pass


class PrelaunchSubscriberUpdate(PrelaunchSubscriberBase):
    email: Optional[EmailStr] = None
    campaign_id: Optional[str] = None
    is_active: Optional[bool] = None
    lead_magnet_sent: Optional[bool] = None


class PrelaunchSubscriber(PrelaunchSubscriberBase):
    id: str
    subscribed_at: datetime
    is_active: bool
    unsubscribed_at: Optional[datetime] = None
    lead_magnet_sent: bool
    lead_magnet_sent_at: Optional[datetime] = None
    user_id: Optional[str] = None
    
    class Config:
        from_attributes = True


# PrelaunchEmailSequence Schemas
class PrelaunchEmailSequenceBase(BaseModel):
    campaign_id: str
    title: str
    description: Optional[str] = None
    is_active: Optional[bool] = True


class PrelaunchEmailSequenceCreate(PrelaunchEmailSequenceBase):
    pass


class PrelaunchEmailSequenceUpdate(PrelaunchEmailSequenceBase):
    campaign_id: Optional[str] = None
    title: Optional[str] = None
    is_active: Optional[bool] = None


class PrelaunchEmailSequence(PrelaunchEmailSequenceBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PrelaunchEmailSequenceWithEmails(PrelaunchEmailSequence):
    emails: List[Dict[str, Any]] = []


# PrelaunchEmail Schemas
class PrelaunchEmailBase(BaseModel):
    sequence_id: str
    subject: str
    body: str
    delay_days: Optional[int] = 0
    is_active: Optional[bool] = True


class PrelaunchEmailCreate(PrelaunchEmailBase):
    pass


class PrelaunchEmailUpdate(PrelaunchEmailBase):
    sequence_id: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    delay_days: Optional[int] = None
    is_active: Optional[bool] = None


class PrelaunchEmail(PrelaunchEmailBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    sent_count: int
    open_count: int
    click_count: int
    
    class Config:
        from_attributes = True


# Association Schemas
class CourseAssociation(BaseModel):
    course_id: str


class BookletAssociation(BaseModel):
    booklet_id: str


class SeriesAssociation(BaseModel):
    series_id: str


# Statistics Update Schema
class CampaignStatisticsUpdate(BaseModel):
    view_count: Optional[int] = 0
    signup_count: Optional[int] = 0
