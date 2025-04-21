from typing import List, Optional, Dict, Any, Union
import uuid
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from app.crud.base import CRUDBase
from app.models.prelaunch import (
    CoursePrelaunchCampaign, PrelaunchSubscriber, 
    PrelaunchEmailSequence, PrelaunchEmail
)
from app.schemas.prelaunch import (
    CoursePrelaunchCampaignCreate, CoursePrelaunchCampaignUpdate,
    PrelaunchSubscriberCreate, PrelaunchSubscriberUpdate,
    PrelaunchEmailSequenceCreate, PrelaunchEmailSequenceUpdate,
    PrelaunchEmailCreate, PrelaunchEmailUpdate,
    CampaignStatisticsUpdate
)


class CRUDCoursePrelaunchCampaign(CRUDBase[CoursePrelaunchCampaign, CoursePrelaunchCampaignCreate, CoursePrelaunchCampaignUpdate]):
    def get_by_slug(self, db: Session, *, slug: str) -> Optional[CoursePrelaunchCampaign]:
        return db.query(CoursePrelaunchCampaign).filter(CoursePrelaunchCampaign.slug == slug).first()
    
    def get_active_campaigns(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[CoursePrelaunchCampaign]:
        """
        Get all active campaigns
        """
        now = datetime.now()
        return db.query(CoursePrelaunchCampaign).filter(
            and_(
                CoursePrelaunchCampaign.is_active == True,
                or_(
                    CoursePrelaunchCampaign.start_date.is_(None),
                    CoursePrelaunchCampaign.start_date <= now
                ),
                or_(
                    CoursePrelaunchCampaign.end_date.is_(None),
                    CoursePrelaunchCampaign.end_date >= now
                )
            )
        ).offset(skip).limit(limit).all()
    
    def get_by_course(self, db: Session, *, course_id: str) -> List[CoursePrelaunchCampaign]:
        """
        Get campaigns associated with a course
        """
        return db.query(CoursePrelaunchCampaign).filter(
            CoursePrelaunchCampaign.courses.any(id=course_id)
        ).all()
    
    def get_by_booklet(self, db: Session, *, booklet_id: str) -> List[CoursePrelaunchCampaign]:
        """
        Get campaigns associated with a booklet
        """
        return db.query(CoursePrelaunchCampaign).filter(
            CoursePrelaunchCampaign.booklets.any(id=booklet_id)
        ).all()
    
    def get_by_series(self, db: Session, *, series_id: str) -> List[CoursePrelaunchCampaign]:
        """
        Get campaigns associated with a series
        """
        return db.query(CoursePrelaunchCampaign).filter(
            CoursePrelaunchCampaign.series.any(id=series_id)
        ).all()
    
    def create(self, db: Session, *, obj_in: CoursePrelaunchCampaignCreate, created_by: Optional[str] = None) -> CoursePrelaunchCampaign:
        """
        Create a new prelaunch campaign
        """
        obj_in_data = obj_in.dict(exclude_unset=True)
        
        # Generate UUID for the campaign
        db_obj = CoursePrelaunchCampaign(
            id=str(uuid.uuid4()),
            created_by=created_by,
            view_count=0,
            signup_count=0,
            conversion_rate=0,
            **obj_in_data
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def add_course(self, db: Session, *, campaign_id: str, course_id: str) -> CoursePrelaunchCampaign:
        """
        Associate a course with a campaign
        """
        from app.models.course import Course
        
        campaign = self.get(db, id=campaign_id)
        course = db.query(Course).filter(Course.id == course_id).first()
        
        if campaign and course:
            campaign.courses.append(course)
            db.commit()
            db.refresh(campaign)
        
        return campaign
    
    def add_booklet(self, db: Session, *, campaign_id: str, booklet_id: str) -> CoursePrelaunchCampaign:
        """
        Associate a booklet with a campaign
        """
        from app.models.booklet import Booklet
        
        campaign = self.get(db, id=campaign_id)
        booklet = db.query(Booklet).filter(Booklet.id == booklet_id).first()
        
        if campaign and booklet:
            campaign.booklets.append(booklet)
            db.commit()
            db.refresh(campaign)
        
        return campaign
    
    def add_series(self, db: Session, *, campaign_id: str, series_id: str) -> CoursePrelaunchCampaign:
        """
        Associate a series with a campaign
        """
        from app.models.series import Series
        
        campaign = self.get(db, id=campaign_id)
        series = db.query(Series).filter(Series.id == series_id).first()
        
        if campaign and series:
            campaign.series.append(series)
            db.commit()
            db.refresh(campaign)
        
        return campaign
    
    def remove_course(self, db: Session, *, campaign_id: str, course_id: str) -> CoursePrelaunchCampaign:
        """
        Remove a course association from a campaign
        """
        from app.models.course import Course
        
        campaign = self.get(db, id=campaign_id)
        course = db.query(Course).filter(Course.id == course_id).first()
        
        if campaign and course and course in campaign.courses:
            campaign.courses.remove(course)
            db.commit()
            db.refresh(campaign)
        
        return campaign
    
    def remove_booklet(self, db: Session, *, campaign_id: str, booklet_id: str) -> CoursePrelaunchCampaign:
        """
        Remove a booklet association from a campaign
        """
        from app.models.booklet import Booklet
        
        campaign = self.get(db, id=campaign_id)
        booklet = db.query(Booklet).filter(Booklet.id == booklet_id).first()
        
        if campaign and booklet and booklet in campaign.booklets:
            campaign.booklets.remove(booklet)
            db.commit()
            db.refresh(campaign)
        
        return campaign
    
    def remove_series(self, db: Session, *, campaign_id: str, series_id: str) -> CoursePrelaunchCampaign:
        """
        Remove a series association from a campaign
        """
        from app.models.series import Series
        
        campaign = self.get(db, id=campaign_id)
        series = db.query(Series).filter(Series.id == series_id).first()
        
        if campaign and series and series in campaign.series:
            campaign.series.remove(series)
            db.commit()
            db.refresh(campaign)
        
        return campaign
    
    def update_statistics(self, db: Session, *, campaign_id: str, stats_in: CampaignStatisticsUpdate) -> CoursePrelaunchCampaign:
        """
        Update campaign statistics
        """
        campaign = self.get(db, id=campaign_id)
        if not campaign:
            return None
        
        # Update statistics
        if stats_in.view_count:
            campaign.view_count += stats_in.view_count
        if stats_in.signup_count:
            campaign.signup_count += stats_in.signup_count
        
        # Calculate conversion rate
        if campaign.view_count > 0:
            campaign.conversion_rate = int((campaign.signup_count / campaign.view_count) * 100)
        
        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        return campaign
    
    def get_with_relations(self, db: Session, *, campaign_id: str) -> Dict[str, Any]:
        """
        Get campaign with all related entities
        """
        campaign = self.get(db, id=campaign_id)
        if not campaign:
            return None
        
        # Get subscribers count
        subscribers_count = db.query(func.count(PrelaunchSubscriber.id)).filter(
            PrelaunchSubscriber.campaign_id == campaign_id,
            PrelaunchSubscriber.is_active == True
        ).scalar()
        
        # Get email sequences
        email_sequences = db.query(PrelaunchEmailSequence).filter(
            PrelaunchEmailSequence.campaign_id == campaign_id
        ).all()
        
        # Build response
        result = campaign.__dict__.copy()
        result["subscribers_count"] = subscribers_count
        result["email_sequences"] = [seq.__dict__ for seq in email_sequences]
        result["courses"] = [course.__dict__ for course in campaign.courses]
        result["booklets"] = [booklet.__dict__ for booklet in campaign.booklets]
        result["series"] = [series.__dict__ for series in campaign.series]
        
        return result


class CRUDPrelaunchSubscriber(CRUDBase[PrelaunchSubscriber, PrelaunchSubscriberCreate, PrelaunchSubscriberUpdate]):
    def get_by_email_and_campaign(self, db: Session, *, email: str, campaign_id: str) -> Optional[PrelaunchSubscriber]:
        return db.query(PrelaunchSubscriber).filter(
            and_(
                PrelaunchSubscriber.email == email,
                PrelaunchSubscriber.campaign_id == campaign_id
            )
        ).first()
    
    def get_by_campaign(self, db: Session, *, campaign_id: str, skip: int = 0, limit: int = 100) -> List[PrelaunchSubscriber]:
        return db.query(PrelaunchSubscriber).filter(
            PrelaunchSubscriber.campaign_id == campaign_id
        ).offset(skip).limit(limit).all()
    
    def get_active_by_campaign(self, db: Session, *, campaign_id: str, skip: int = 0, limit: int = 100) -> List[PrelaunchSubscriber]:
        return db.query(PrelaunchSubscriber).filter(
            and_(
                PrelaunchSubscriber.campaign_id == campaign_id,
                PrelaunchSubscriber.is_active == True
            )
        ).offset(skip).limit(limit).all()
    
    def create(self, db: Session, *, obj_in: PrelaunchSubscriberCreate, user_id: Optional[str] = None) -> PrelaunchSubscriber:
        """
        Create a new prelaunch subscriber
        """
        # Check if subscriber already exists
        existing = self.get_by_email_and_campaign(db, email=obj_in.email, campaign_id=obj_in.campaign_id)
        if existing:
            # If it exists but was unsubscribed, reactivate it
            if not existing.is_active:
                existing.is_active = True
                existing.unsubscribed_at = None
                db.add(existing)
                db.commit()
                db.refresh(existing)
            return existing
        
        # Create new subscriber
        obj_in_data = obj_in.dict(exclude_unset=True)
        
        db_obj = PrelaunchSubscriber(
            id=str(uuid.uuid4()),
            user_id=user_id,
            is_active=True,
            lead_magnet_sent=False,
            **obj_in_data
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Update campaign statistics
        campaign = db.query(CoursePrelaunchCampaign).filter(CoursePrelaunchCampaign.id == obj_in.campaign_id).first()
        if campaign:
            campaign.signup_count += 1
            if campaign.view_count > 0:
                campaign.conversion_rate = int((campaign.signup_count / campaign.view_count) * 100)
            db.add(campaign)
            db.commit()
        
        return db_obj
    
    def unsubscribe(self, db: Session, *, email: str, campaign_id: str) -> Optional[PrelaunchSubscriber]:
        subscriber = self.get_by_email_and_campaign(db, email=email, campaign_id=campaign_id)
        if subscriber:
            subscriber.is_active = False
            subscriber.unsubscribed_at = datetime.now()
            db.add(subscriber)
            db.commit()
            db.refresh(subscriber)
        return subscriber
    
    def mark_lead_magnet_sent(self, db: Session, *, subscriber_id: str) -> PrelaunchSubscriber:
        subscriber = self.get(db, id=subscriber_id)
        if subscriber:
            subscriber.lead_magnet_sent = True
            subscriber.lead_magnet_sent_at = datetime.now()
            db.add(subscriber)
            db.commit()
            db.refresh(subscriber)
        return subscriber


class CRUDPrelaunchEmailSequence(CRUDBase[PrelaunchEmailSequence, PrelaunchEmailSequenceCreate, PrelaunchEmailSequenceUpdate]):
    def get_by_campaign(self, db: Session, *, campaign_id: str) -> List[PrelaunchEmailSequence]:
        return db.query(PrelaunchEmailSequence).filter(
            PrelaunchEmailSequence.campaign_id == campaign_id
        ).all()
    
    def create(self, db: Session, *, obj_in: PrelaunchEmailSequenceCreate) -> PrelaunchEmailSequence:
        """
        Create a new email sequence
        """
        obj_in_data = obj_in.dict(exclude_unset=True)
        
        db_obj = PrelaunchEmailSequence(
            id=str(uuid.uuid4()),
            **obj_in_data
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_with_emails(self, db: Session, *, sequence_id: str) -> Dict[str, Any]:
        """
        Get sequence with all emails
        """
        sequence = self.get(db, id=sequence_id)
        if not sequence:
            return None
        
        # Get emails
        emails = db.query(PrelaunchEmail).filter(
            PrelaunchEmail.sequence_id == sequence_id
        ).order_by(PrelaunchEmail.delay_days).all()
        
        # Build response
        result = sequence.__dict__.copy()
        result["emails"] = [email.__dict__ for email in emails]
        
        return result


class CRUDPrelaunchEmail(CRUDBase[PrelaunchEmail, PrelaunchEmailCreate, PrelaunchEmailUpdate]):
    def get_by_sequence(self, db: Session, *, sequence_id: str) -> List[PrelaunchEmail]:
        return db.query(PrelaunchEmail).filter(
            PrelaunchEmail.sequence_id == sequence_id
        ).order_by(PrelaunchEmail.delay_days).all()
    
    def create(self, db: Session, *, obj_in: PrelaunchEmailCreate) -> PrelaunchEmail:
        """
        Create a new email in a sequence
        """
        obj_in_data = obj_in.dict(exclude_unset=True)
        
        db_obj = PrelaunchEmail(
            id=str(uuid.uuid4()),
            sent_count=0,
            open_count=0,
            click_count=0,
            **obj_in_data
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update_statistics(self, db: Session, *, email_id: str, sent: int = 0, opened: int = 0, clicked: int = 0) -> PrelaunchEmail:
        """
        Update email statistics
        """
        email = self.get(db, id=email_id)
        if not email:
            return None
        
        # Update statistics
        if sent:
            email.sent_count += sent
        if opened:
            email.open_count += opened
        if clicked:
            email.click_count += clicked
        
        db.add(email)
        db.commit()
        db.refresh(email)
        return email


course_prelaunch_campaign = CRUDCoursePrelaunchCampaign(CoursePrelaunchCampaign)
prelaunch_subscriber = CRUDPrelaunchSubscriber(PrelaunchSubscriber)
prelaunch_email_sequence = CRUDPrelaunchEmailSequence(PrelaunchEmailSequence)
prelaunch_email = CRUDPrelaunchEmail(PrelaunchEmail)
