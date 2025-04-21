from typing import List, Optional, Dict, Any, Union
import uuid
from datetime import datetime
import httpx
import json
import os

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from app.crud.base import CRUDBase
from app.models.marketing import NewsletterSubscription, MarketingBanner
from app.schemas.marketing import (
    NewsletterSubscriptionCreate, NewsletterSubscriptionUpdate,
    MarketingBannerCreate, MarketingBannerUpdate, BannerStatisticsUpdate
)


class CRUDNewsletterSubscription(CRUDBase[NewsletterSubscription, NewsletterSubscriptionCreate, NewsletterSubscriptionUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[NewsletterSubscription]:
        return db.query(NewsletterSubscription).filter(NewsletterSubscription.email == email).first()

    def get_active_subscriptions(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[NewsletterSubscription]:
        return db.query(NewsletterSubscription).filter(
            NewsletterSubscription.is_active == True
        ).offset(skip).limit(limit).all()

    def get_unsynced_subscriptions(self, db: Session) -> List[NewsletterSubscription]:
        return db.query(NewsletterSubscription).filter(
            and_(
                NewsletterSubscription.is_active == True,
                NewsletterSubscription.synced_to_kit == False
            )
        ).all()

    def create(self, db: Session, *, obj_in: NewsletterSubscriptionCreate) -> NewsletterSubscription:
        # Check if email already exists
        existing = self.get_by_email(db, email=obj_in.email)
        if existing:
            # If it exists but was unsubscribed, reactivate it
            if not existing.is_active:
                existing.is_active = True
                existing.unsubscribed_at = None
                db.add(existing)
                db.commit()
                db.refresh(existing)
            return existing

        # Create new subscription
        db_obj = NewsletterSubscription(
            id=str(uuid.uuid4()),
            email=obj_in.email,
            name=obj_in.name,
            source=obj_in.source,
            is_active=True,
            synced_to_kit=False,
            subscription_metadata=obj_in.metadata
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        # Try to sync to Kit.com
        self.sync_to_kit(db, subscription=db_obj)

        return db_obj

    def unsubscribe(self, db: Session, *, email: str) -> Optional[NewsletterSubscription]:
        subscription = self.get_by_email(db, email=email)
        if subscription:
            subscription.is_active = False
            subscription.unsubscribed_at = datetime.now()
            db.add(subscription)
            db.commit()
            db.refresh(subscription)
        return subscription

    def sync_to_kit(self, db: Session, *, subscription: NewsletterSubscription) -> bool:
        """
        Sync a subscription to Kit.com
        """
        if subscription.synced_to_kit:
            return True

        # Kit.com API details
        api_key = "rOcS85r9XTeJ0-Et_A1laQ"
        list_name = "codessnipetsMailing"

        try:
            # Prepare the data for Kit.com API
            data = {
                "email": subscription.email,
                "name": subscription.name or "",
                "source": subscription.source or "website",
                "metadata": subscription.metadata or {}
            }

            # Make the API request to Kit.com
            # Note: This is a placeholder. You'll need to implement the actual API call
            # based on Kit.com's API documentation
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            # Placeholder URL - replace with actual Kit.com API endpoint
            url = f"https://api.kit.com/lists/{list_name}/subscribers"

            # Uncomment this when ready to make actual API calls
            # response = httpx.post(url, json=data, headers=headers)
            # if response.status_code in (200, 201):
            #     # Update subscription as synced
            #     subscription.synced_to_kit = True
            #     subscription.kit_sync_at = datetime.now()
            #     db.add(subscription)
            #     db.commit()
            #     db.refresh(subscription)
            #     return True

            # For now, simulate successful sync
            subscription.synced_to_kit = True
            subscription.kit_sync_at = datetime.now()
            db.add(subscription)
            db.commit()
            db.refresh(subscription)
            return True

        except Exception as e:
            print(f"Error syncing to Kit.com: {e}")
            return False

    def sync_all_unsynced(self, db: Session) -> int:
        """
        Sync all unsynced subscriptions to Kit.com
        Returns the number of successfully synced subscriptions
        """
        unsynced = self.get_unsynced_subscriptions(db)
        synced_count = 0

        for subscription in unsynced:
            if self.sync_to_kit(db, subscription=subscription):
                synced_count += 1

        return synced_count


class CRUDMarketingBanner(CRUDBase[MarketingBanner, MarketingBannerCreate, MarketingBannerUpdate]):
    def get_active_banners(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[MarketingBanner]:
        """
        Get all active banners
        """
        now = datetime.now()
        return db.query(MarketingBanner).filter(
            and_(
                MarketingBanner.is_active == True,
                or_(
                    MarketingBanner.start_date.is_(None),
                    MarketingBanner.start_date <= now
                ),
                or_(
                    MarketingBanner.end_date.is_(None),
                    MarketingBanner.end_date >= now
                )
            )
        ).order_by(desc(MarketingBanner.priority)).offset(skip).limit(limit).all()

    def get_banners_for_page(self, db: Session, *, page: str, is_logged_in: bool) -> List[MarketingBanner]:
        """
        Get active banners for a specific page
        """
        now = datetime.now()
        query = db.query(MarketingBanner).filter(
            and_(
                MarketingBanner.is_active == True,
                or_(
                    MarketingBanner.start_date.is_(None),
                    MarketingBanner.start_date <= now
                ),
                or_(
                    MarketingBanner.end_date.is_(None),
                    MarketingBanner.end_date >= now
                )
            )
        )

        # Filter by user login status
        if is_logged_in:
            query = query.filter(MarketingBanner.show_to_logged_in == True)
        else:
            query = query.filter(MarketingBanner.show_to_anonymous == True)

        # Filter by page
        query = query.filter(
            or_(
                MarketingBanner.show_on_pages.is_(None),
                MarketingBanner.show_on_pages.contains([page])
            )
        )

        return query.order_by(desc(MarketingBanner.priority)).all()

    def create(self, db: Session, *, obj_in: MarketingBannerCreate, created_by: Optional[str] = None) -> MarketingBanner:
        """
        Create a new marketing banner
        """
        obj_in_data = obj_in.dict()

        # Generate UUID for the banner
        db_obj = MarketingBanner(
            id=str(uuid.uuid4()),
            created_by=created_by,
            impressions=0,
            clicks=0,
            dismissals=0,
            conversions=0,
            **obj_in_data
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_statistics(self, db: Session, *, banner_id: str, stats_in: BannerStatisticsUpdate) -> MarketingBanner:
        """
        Update banner statistics
        """
        banner = self.get(db, id=banner_id)
        if not banner:
            return None

        # Update statistics
        if stats_in.impressions:
            banner.impressions += stats_in.impressions
        if stats_in.clicks:
            banner.clicks += stats_in.clicks
        if stats_in.dismissals:
            banner.dismissals += stats_in.dismissals
        if stats_in.conversions:
            banner.conversions += stats_in.conversions

        db.add(banner)
        db.commit()
        db.refresh(banner)
        return banner


newsletter_subscription = CRUDNewsletterSubscription(NewsletterSubscription)
marketing_banner = CRUDMarketingBanner(MarketingBanner)
