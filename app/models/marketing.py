from sqlalchemy import Boolean, Column, String, DateTime, Text, JSON, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class NewsletterSubscription(Base):
    __tablename__ = "newsletter_subscriptions"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    subscribed_at = Column(DateTime(timezone=True), server_default=func.now)
    unsubscribed_at = Column(DateTime(timezone=True), nullable=True)
    source = Column(String, nullable=True)  # Where the subscription came from (e.g., 'homepage', 'blog', 'course')
    synced_to_kit = Column(Boolean, default=False)  # Whether the subscription has been synced to Kit.com
    kit_sync_at = Column(DateTime(timezone=True), nullable=True)  # When the subscription was synced to Kit.com
    subscription_metadata = Column(JSON, nullable=True)  # Additional metadata about the subscription

    # Relationship with User (optional - if the subscriber is a registered user)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    user = relationship("User", backref="newsletter_subscriptions")


class MarketingBanner(Base):
    __tablename__ = "marketing_banners"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    cta_text = Column(String, nullable=True)  # Call to action button text
    cta_link = Column(String, nullable=True)  # Call to action button link
    banner_type = Column(String, default="banner")  # 'banner', 'popover', 'notification'
    position = Column(String, default="top")  # 'top', 'bottom', 'left', 'right', 'center'
    background_color = Column(String, default="#f8f9fa")
    text_color = Column(String, default="#212529")
    is_active = Column(Boolean, default=True)

    # Targeting
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    show_to_logged_in = Column(Boolean, default=True)  # Show to logged-in users
    show_to_anonymous = Column(Boolean, default=True)  # Show to anonymous users
    show_once_per_session = Column(Boolean, default=False)  # Show only once per session
    show_on_pages = Column(JSON, nullable=True)  # List of pages to show on (e.g., ['home', 'blog', 'courses'])
    priority = Column(Integer, default=0)  # Higher priority banners are shown first

    # Tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now)
    created_by = Column(String, ForeignKey("users.id"), nullable=True)

    # Relationships
    creator = relationship("User", backref="created_banners")

    # Statistics
    impressions = Column(Integer, default=0)  # Number of times the banner was shown
    clicks = Column(Integer, default=0)  # Number of times the CTA was clicked
    dismissals = Column(Integer, default=0)  # Number of times the banner was dismissed
    conversions = Column(Integer, default=0)  # Number of times the banner led to a conversion
