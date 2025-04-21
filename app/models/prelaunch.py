from sqlalchemy import Boolean, Column, String, DateTime, Text, JSON, ForeignKey, Integer, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


# Association tables for different content types
prelaunch_course_association = Table(
    "prelaunch_course_association",
    Base.metadata,
    Column("prelaunch_id", String, ForeignKey("course_prelaunch_campaigns.id"), primary_key=True),
    Column("course_id", String, ForeignKey("courses.id"), primary_key=True)
)

prelaunch_booklet_association = Table(
    "prelaunch_booklet_association",
    Base.metadata,
    Column("prelaunch_id", String, ForeignKey("course_prelaunch_campaigns.id"), primary_key=True),
    Column("booklet_id", String, ForeignKey("booklets.id"), primary_key=True)
)

prelaunch_series_association = Table(
    "prelaunch_series_association",
    Base.metadata,
    Column("prelaunch_id", String, ForeignKey("course_prelaunch_campaigns.id"), primary_key=True),
    Column("series_id", String, ForeignKey("series.id"), primary_key=True)
)


class CoursePrelaunchCampaign(Base):
    """
    Model for course prelaunch campaigns, which can be associated with courses, booklets, or series.
    Used for creating lead magnets and prelaunch enrollment landing pages.
    """
    __tablename__ = "course_prelaunch_campaigns"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)

    # Campaign details
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)

    # Lead magnet details
    lead_magnet_title = Column(String, nullable=True)
    lead_magnet_description = Column(Text, nullable=True)
    lead_magnet_file_url = Column(String, nullable=True)

    # Landing page content
    header_image_url = Column(String, nullable=True)
    content = Column(Text, nullable=True)  # Rich text content for the landing page
    cta_text = Column(String, nullable=True)  # Call to action button text
    cta_url = Column(String, nullable=True)  # Call to action button URL

    # Pricing and enrollment details
    early_bird_price = Column(Integer, nullable=True)  # In cents
    regular_price = Column(Integer, nullable=True)  # In cents
    max_enrollments = Column(Integer, nullable=True)  # Maximum number of enrollments

    # Campaign statistics
    view_count = Column(Integer, default=0)
    signup_count = Column(Integer, default=0)
    conversion_rate = Column(Integer, default=0)  # Calculated as (signup_count / view_count) * 100

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now)
    created_by = Column(String, ForeignKey("users.id"), nullable=True)

    # Relationships
    creator = relationship("User", backref="created_prelaunch_campaigns")

    # Content relationships
    courses = relationship("Course", secondary=prelaunch_course_association, backref="prelaunch_campaigns")
    booklets = relationship("Booklet", secondary=prelaunch_booklet_association, backref="prelaunch_campaigns")
    series = relationship("Series", secondary=prelaunch_series_association, backref="prelaunch_campaigns")

    # Subscribers relationship
    subscribers = relationship("PrelaunchSubscriber", back_populates="campaign")


class PrelaunchSubscriber(Base):
    """
    Model for subscribers to prelaunch campaigns.
    """
    __tablename__ = "prelaunch_subscribers"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, nullable=False, index=True)
    name = Column(String, nullable=True)

    # Subscription details
    campaign_id = Column(String, ForeignKey("course_prelaunch_campaigns.id"), nullable=False)
    subscribed_at = Column(DateTime(timezone=True), server_default=func.now)
    is_active = Column(Boolean, default=True)
    unsubscribed_at = Column(DateTime(timezone=True), nullable=True)

    # Lead magnet delivery
    lead_magnet_sent = Column(Boolean, default=False)
    lead_magnet_sent_at = Column(DateTime(timezone=True), nullable=True)

    # User association (optional)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)

    # Tracking
    source = Column(String, nullable=True)  # Where the subscription came from
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    referrer = Column(String, nullable=True)

    # Custom fields (for additional data collection)
    custom_fields = Column(JSON, nullable=True)

    # Relationships
    campaign = relationship("CoursePrelaunchCampaign", back_populates="subscribers")
    user = relationship("User", backref="prelaunch_subscriptions")


class PrelaunchEmailSequence(Base):
    """
    Model for email sequences associated with prelaunch campaigns.
    """
    __tablename__ = "prelaunch_email_sequences"

    id = Column(String, primary_key=True, index=True)
    campaign_id = Column(String, ForeignKey("course_prelaunch_campaigns.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    # Sequence details
    is_active = Column(Boolean, default=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now)

    # Relationships
    campaign = relationship("CoursePrelaunchCampaign", backref="email_sequences")
    emails = relationship("PrelaunchEmail", back_populates="sequence")


class PrelaunchEmail(Base):
    """
    Model for individual emails in a prelaunch email sequence.
    """
    __tablename__ = "prelaunch_emails"

    id = Column(String, primary_key=True, index=True)
    sequence_id = Column(String, ForeignKey("prelaunch_email_sequences.id"), nullable=False)

    # Email content
    subject = Column(String, nullable=False)
    body = Column(Text, nullable=False)

    # Sending details
    delay_days = Column(Integer, default=0)  # Days after subscription to send
    is_active = Column(Boolean, default=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now)

    # Statistics
    sent_count = Column(Integer, default=0)
    open_count = Column(Integer, default=0)
    click_count = Column(Integer, default=0)

    # Relationships
    sequence = relationship("PrelaunchEmailSequence", back_populates="emails")
