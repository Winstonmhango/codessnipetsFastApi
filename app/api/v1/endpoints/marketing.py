from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


# Newsletter Subscription endpoints
@router.post("/newsletter/subscribe", response_model=schemas.NewsletterSubscription)
def subscribe_to_newsletter(
    *,
    db: Session = Depends(deps.get_db),
    subscription_in: schemas.NewsletterSubscriptionCreate,
    current_user: Optional[models.User] = Depends(deps.get_current_user_optional),
) -> Any:
    """
    Subscribe to the newsletter.
    """
    # If user is logged in, associate the subscription with the user
    user_id = current_user.id if current_user else None
    
    # Create subscription
    subscription = crud.newsletter_subscription.create(db, obj_in=subscription_in)
    
    # If user is logged in, associate the subscription with the user
    if user_id and subscription:
        subscription.user_id = user_id
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
    
    return subscription


@router.post("/newsletter/unsubscribe", response_model=schemas.NewsletterSubscription)
def unsubscribe_from_newsletter(
    *,
    db: Session = Depends(deps.get_db),
    email: str = Body(..., embed=True),
) -> Any:
    """
    Unsubscribe from the newsletter.
    """
    subscription = crud.newsletter_subscription.unsubscribe(db, email=email)
    if not subscription:
        raise HTTPException(
            status_code=404,
            detail="Email not found in subscription list",
        )
    return subscription


@router.get("/newsletter/subscriptions", response_model=List[schemas.NewsletterSubscription])
def read_newsletter_subscriptions(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve newsletter subscriptions.
    """
    subscriptions = crud.newsletter_subscription.get_active_subscriptions(
        db, skip=skip, limit=limit
    )
    return subscriptions


@router.post("/newsletter/sync", response_model=dict)
def sync_newsletter_subscriptions(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Sync unsynced newsletter subscriptions to Kit.com.
    """
    synced_count = crud.newsletter_subscription.sync_all_unsynced(db)
    return {"synced_count": synced_count}


# Marketing Banner endpoints
@router.post("/banners", response_model=schemas.MarketingBanner)
def create_marketing_banner(
    *,
    db: Session = Depends(deps.get_db),
    banner_in: schemas.MarketingBannerCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new marketing banner.
    """
    banner = crud.marketing_banner.create(
        db, obj_in=banner_in, created_by=current_user.id
    )
    return banner


@router.get("/banners", response_model=List[schemas.MarketingBanner])
def read_marketing_banners(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve marketing banners.
    """
    banners = crud.marketing_banner.get_multi(db, skip=skip, limit=limit)
    return banners


@router.get("/banners/active", response_model=List[schemas.MarketingBanner])
def read_active_marketing_banners(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve active marketing banners.
    """
    banners = crud.marketing_banner.get_active_banners(db, skip=skip, limit=limit)
    return banners


@router.get("/banners/page/{page}", response_model=List[schemas.MarketingBanner])
def read_marketing_banners_for_page(
    *,
    db: Session = Depends(deps.get_db),
    page: str = Path(..., title="The page to get banners for"),
    current_user: Optional[models.User] = Depends(deps.get_current_user_optional),
) -> Any:
    """
    Retrieve marketing banners for a specific page.
    """
    is_logged_in = current_user is not None
    banners = crud.marketing_banner.get_banners_for_page(
        db, page=page, is_logged_in=is_logged_in
    )
    return banners


@router.get("/banners/{banner_id}", response_model=schemas.MarketingBanner)
def read_marketing_banner(
    *,
    db: Session = Depends(deps.get_db),
    banner_id: str = Path(..., title="The ID of the banner to get"),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get marketing banner by ID.
    """
    banner = crud.marketing_banner.get(db, id=banner_id)
    if not banner:
        raise HTTPException(status_code=404, detail="Banner not found")
    return banner


@router.put("/banners/{banner_id}", response_model=schemas.MarketingBanner)
def update_marketing_banner(
    *,
    db: Session = Depends(deps.get_db),
    banner_id: str = Path(..., title="The ID of the banner to update"),
    banner_in: schemas.MarketingBannerUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a marketing banner.
    """
    banner = crud.marketing_banner.get(db, id=banner_id)
    if not banner:
        raise HTTPException(status_code=404, detail="Banner not found")
    banner = crud.marketing_banner.update(db, db_obj=banner, obj_in=banner_in)
    return banner


@router.delete("/banners/{banner_id}", response_model=schemas.MarketingBanner)
def delete_marketing_banner(
    *,
    db: Session = Depends(deps.get_db),
    banner_id: str = Path(..., title="The ID of the banner to delete"),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a marketing banner.
    """
    banner = crud.marketing_banner.get(db, id=banner_id)
    if not banner:
        raise HTTPException(status_code=404, detail="Banner not found")
    banner = crud.marketing_banner.remove(db, id=banner_id)
    return banner


@router.post("/banners/{banner_id}/stats", response_model=schemas.MarketingBanner)
def update_banner_statistics(
    *,
    db: Session = Depends(deps.get_db),
    banner_id: str = Path(..., title="The ID of the banner to update statistics for"),
    stats_in: schemas.BannerStatisticsUpdate,
) -> Any:
    """
    Update banner statistics.
    """
    banner = crud.marketing_banner.update_statistics(db, banner_id=banner_id, stats_in=stats_in)
    if not banner:
        raise HTTPException(status_code=404, detail="Banner not found")
    return banner
