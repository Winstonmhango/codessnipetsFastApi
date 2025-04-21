from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


# Newsletter Subscription Schemas
class NewsletterSubscriptionBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    source: Optional[str] = None
    is_active: Optional[bool] = True
    metadata: Optional[Dict[str, Any]] = None  # Will be stored in subscription_metadata


class NewsletterSubscriptionCreate(NewsletterSubscriptionBase):
    pass


class NewsletterSubscriptionUpdate(NewsletterSubscriptionBase):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class NewsletterSubscription(NewsletterSubscriptionBase):
    id: str
    subscribed_at: datetime
    unsubscribed_at: Optional[datetime] = None
    synced_to_kit: bool
    kit_sync_at: Optional[datetime] = None
    user_id: Optional[str] = None
    subscription_metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


# Marketing Banner Schemas
class MarketingBannerBase(BaseModel):
    title: str
    content: str
    cta_text: Optional[str] = None
    cta_link: Optional[str] = None
    banner_type: Optional[str] = "banner"
    position: Optional[str] = "top"
    background_color: Optional[str] = "#f8f9fa"
    text_color: Optional[str] = "#212529"
    is_active: Optional[bool] = True

    # Targeting
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    show_to_logged_in: Optional[bool] = True
    show_to_anonymous: Optional[bool] = True
    show_once_per_session: Optional[bool] = False
    show_on_pages: Optional[List[str]] = None
    priority: Optional[int] = 0


class MarketingBannerCreate(MarketingBannerBase):
    pass


class MarketingBannerUpdate(MarketingBannerBase):
    title: Optional[str] = None
    content: Optional[str] = None


class MarketingBanner(MarketingBannerBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    impressions: int
    clicks: int
    dismissals: int
    conversions: int

    class Config:
        from_attributes = True


# Banner Statistics Schema
class BannerStatisticsUpdate(BaseModel):
    impressions: Optional[int] = 0
    clicks: Optional[int] = 0
    dismissals: Optional[int] = 0
    conversions: Optional[int] = 0
