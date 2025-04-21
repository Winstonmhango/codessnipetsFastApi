from typing import Any, List, Optional, Dict

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


# CoursePrelaunchCampaign endpoints
@router.get("/campaigns/", response_model=List[schemas.CoursePrelaunchCampaign])
def read_prelaunch_campaigns(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve prelaunch campaigns.
    """
    if active_only:
        campaigns = crud.course_prelaunch_campaign.get_active_campaigns(db, skip=skip, limit=limit)
    else:
        campaigns = crud.course_prelaunch_campaign.get_multi(db, skip=skip, limit=limit)
    return campaigns


@router.post("/campaigns/", response_model=schemas.CoursePrelaunchCampaign)
def create_prelaunch_campaign(
    *,
    db: Session = Depends(deps.get_db),
    campaign_in: schemas.CoursePrelaunchCampaignCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new prelaunch campaign.
    """
    # Check if slug already exists
    campaign = crud.course_prelaunch_campaign.get_by_slug(db, slug=campaign_in.slug)
    if campaign:
        raise HTTPException(
            status_code=400,
            detail="Campaign with this slug already exists",
        )
    campaign = crud.course_prelaunch_campaign.create(
        db, obj_in=campaign_in, created_by=current_user.id
    )
    return campaign


@router.get("/campaigns/{campaign_id}", response_model=schemas.CoursePrelaunchCampaignWithRelations)
def read_prelaunch_campaign(
    *,
    db: Session = Depends(deps.get_db),
    campaign_id: str = Path(..., title="The ID of the campaign to get"),
    current_user: Optional[models.User] = Depends(deps.get_current_user_optional),
) -> Any:
    """
    Get prelaunch campaign by ID.
    """
    campaign = crud.course_prelaunch_campaign.get(db, id=campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # If not superuser, only allow access to active campaigns
    if not (current_user and current_user.is_superuser):
        if not campaign.is_active:
            raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Get campaign with relations
    campaign_data = crud.course_prelaunch_campaign.get_with_relations(db, campaign_id=campaign_id)
    
    # Track view if not superuser
    if not (current_user and current_user.is_superuser):
        stats_update = schemas.CampaignStatisticsUpdate(view_count=1)
        crud.course_prelaunch_campaign.update_statistics(
            db, campaign_id=campaign_id, stats_in=stats_update
        )
    
    return campaign_data


@router.put("/campaigns/{campaign_id}", response_model=schemas.CoursePrelaunchCampaign)
def update_prelaunch_campaign(
    *,
    db: Session = Depends(deps.get_db),
    campaign_id: str = Path(..., title="The ID of the campaign to update"),
    campaign_in: schemas.CoursePrelaunchCampaignUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a prelaunch campaign.
    """
    campaign = crud.course_prelaunch_campaign.get(db, id=campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Check if slug already exists (if updating slug)
    if campaign_in.slug and campaign_in.slug != campaign.slug:
        existing = crud.course_prelaunch_campaign.get_by_slug(db, slug=campaign_in.slug)
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Campaign with this slug already exists",
            )
    
    campaign = crud.course_prelaunch_campaign.update(db, db_obj=campaign, obj_in=campaign_in)
    return campaign


@router.delete("/campaigns/{campaign_id}", response_model=schemas.CoursePrelaunchCampaign)
def delete_prelaunch_campaign(
    *,
    db: Session = Depends(deps.get_db),
    campaign_id: str = Path(..., title="The ID of the campaign to delete"),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a prelaunch campaign.
    """
    campaign = crud.course_prelaunch_campaign.get(db, id=campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Check if campaign has subscribers
    subscribers = crud.prelaunch_subscriber.get_by_campaign(db, campaign_id=campaign_id)
    if subscribers:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete campaign with subscribers. Deactivate it instead.",
        )
    
    campaign = crud.course_prelaunch_campaign.remove(db, id=campaign_id)
    return campaign


@router.post("/campaigns/{campaign_id}/courses", response_model=schemas.CoursePrelaunchCampaign)
def add_course_to_campaign(
    *,
    db: Session = Depends(deps.get_db),
    campaign_id: str = Path(..., title="The ID of the campaign"),
    course_association: schemas.CourseAssociation,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Add a course to a prelaunch campaign.
    """
    campaign = crud.course_prelaunch_campaign.get(db, id=campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    course = crud.course.get(db, id=course_association.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    campaign = crud.course_prelaunch_campaign.add_course(
        db, campaign_id=campaign_id, course_id=course_association.course_id
    )
    return campaign


@router.post("/campaigns/{campaign_id}/booklets", response_model=schemas.CoursePrelaunchCampaign)
def add_booklet_to_campaign(
    *,
    db: Session = Depends(deps.get_db),
    campaign_id: str = Path(..., title="The ID of the campaign"),
    booklet_association: schemas.BookletAssociation,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Add a booklet to a prelaunch campaign.
    """
    campaign = crud.course_prelaunch_campaign.get(db, id=campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    booklet = crud.booklet.get(db, id=booklet_association.booklet_id)
    if not booklet:
        raise HTTPException(status_code=404, detail="Booklet not found")
    
    campaign = crud.course_prelaunch_campaign.add_booklet(
        db, campaign_id=campaign_id, booklet_id=booklet_association.booklet_id
    )
    return campaign


@router.post("/campaigns/{campaign_id}/series", response_model=schemas.CoursePrelaunchCampaign)
def add_series_to_campaign(
    *,
    db: Session = Depends(deps.get_db),
    campaign_id: str = Path(..., title="The ID of the campaign"),
    series_association: schemas.SeriesAssociation,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Add a series to a prelaunch campaign.
    """
    campaign = crud.course_prelaunch_campaign.get(db, id=campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    series_obj = crud.series.get(db, id=series_association.series_id)
    if not series_obj:
        raise HTTPException(status_code=404, detail="Series not found")
    
    campaign = crud.course_prelaunch_campaign.add_series(
        db, campaign_id=campaign_id, series_id=series_association.series_id
    )
    return campaign


@router.delete("/campaigns/{campaign_id}/courses/{course_id}", response_model=schemas.CoursePrelaunchCampaign)
def remove_course_from_campaign(
    *,
    db: Session = Depends(deps.get_db),
    campaign_id: str = Path(..., title="The ID of the campaign"),
    course_id: str = Path(..., title="The ID of the course"),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Remove a course from a prelaunch campaign.
    """
    campaign = crud.course_prelaunch_campaign.get(db, id=campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign = crud.course_prelaunch_campaign.remove_course(
        db, campaign_id=campaign_id, course_id=course_id
    )
    return campaign


@router.delete("/campaigns/{campaign_id}/booklets/{booklet_id}", response_model=schemas.CoursePrelaunchCampaign)
def remove_booklet_from_campaign(
    *,
    db: Session = Depends(deps.get_db),
    campaign_id: str = Path(..., title="The ID of the campaign"),
    booklet_id: str = Path(..., title="The ID of the booklet"),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Remove a booklet from a prelaunch campaign.
    """
    campaign = crud.course_prelaunch_campaign.get(db, id=campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign = crud.course_prelaunch_campaign.remove_booklet(
        db, campaign_id=campaign_id, booklet_id=booklet_id
    )
    return campaign


@router.delete("/campaigns/{campaign_id}/series/{series_id}", response_model=schemas.CoursePrelaunchCampaign)
def remove_series_from_campaign(
    *,
    db: Session = Depends(deps.get_db),
    campaign_id: str = Path(..., title="The ID of the campaign"),
    series_id: str = Path(..., title="The ID of the series"),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Remove a series from a prelaunch campaign.
    """
    campaign = crud.course_prelaunch_campaign.get(db, id=campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign = crud.course_prelaunch_campaign.remove_series(
        db, campaign_id=campaign_id, series_id=series_id
    )
    return campaign


@router.post("/campaigns/{campaign_id}/stats", response_model=schemas.CoursePrelaunchCampaign)
def update_campaign_statistics(
    *,
    db: Session = Depends(deps.get_db),
    campaign_id: str = Path(..., title="The ID of the campaign"),
    stats_in: schemas.CampaignStatisticsUpdate,
) -> Any:
    """
    Update campaign statistics.
    """
    campaign = crud.course_prelaunch_campaign.update_statistics(
        db, campaign_id=campaign_id, stats_in=stats_in
    )
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


# PrelaunchSubscriber endpoints
@router.post("/subscribe", response_model=schemas.PrelaunchSubscriber)
def subscribe_to_campaign(
    *,
    db: Session = Depends(deps.get_db),
    subscriber_in: schemas.PrelaunchSubscriberCreate,
    current_user: Optional[models.User] = Depends(deps.get_current_user_optional),
) -> Any:
    """
    Subscribe to a prelaunch campaign.
    """
    # Check if campaign exists and is active
    campaign = crud.course_prelaunch_campaign.get(db, id=subscriber_in.campaign_id)
    if not campaign or not campaign.is_active:
        raise HTTPException(status_code=404, detail="Campaign not found or inactive")
    
    # If user is logged in, associate the subscription with the user
    user_id = current_user.id if current_user else None
    
    # Create subscription
    subscriber = crud.prelaunch_subscriber.create(db, obj_in=subscriber_in, user_id=user_id)
    
    return subscriber


@router.post("/unsubscribe", response_model=schemas.PrelaunchSubscriber)
def unsubscribe_from_campaign(
    *,
    db: Session = Depends(deps.get_db),
    email: str = Body(..., embed=True),
    campaign_id: str = Body(..., embed=True),
) -> Any:
    """
    Unsubscribe from a prelaunch campaign.
    """
    subscriber = crud.prelaunch_subscriber.unsubscribe(db, email=email, campaign_id=campaign_id)
    if not subscriber:
        raise HTTPException(
            status_code=404,
            detail="Email not found in campaign subscription list",
        )
    return subscriber


@router.get("/campaigns/{campaign_id}/subscribers", response_model=List[schemas.PrelaunchSubscriber])
def read_campaign_subscribers(
    *,
    db: Session = Depends(deps.get_db),
    campaign_id: str = Path(..., title="The ID of the campaign"),
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve subscribers for a campaign.
    """
    campaign = crud.course_prelaunch_campaign.get(db, id=campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if active_only:
        subscribers = crud.prelaunch_subscriber.get_active_by_campaign(
            db, campaign_id=campaign_id, skip=skip, limit=limit
        )
    else:
        subscribers = crud.prelaunch_subscriber.get_by_campaign(
            db, campaign_id=campaign_id, skip=skip, limit=limit
        )
    
    return subscribers


@router.post("/subscribers/{subscriber_id}/lead-magnet-sent", response_model=schemas.PrelaunchSubscriber)
def mark_lead_magnet_sent(
    *,
    db: Session = Depends(deps.get_db),
    subscriber_id: str = Path(..., title="The ID of the subscriber"),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Mark lead magnet as sent for a subscriber.
    """
    subscriber = crud.prelaunch_subscriber.mark_lead_magnet_sent(db, subscriber_id=subscriber_id)
    if not subscriber:
        raise HTTPException(status_code=404, detail="Subscriber not found")
    return subscriber


# PrelaunchEmailSequence endpoints
@router.get("/campaigns/{campaign_id}/email-sequences", response_model=List[schemas.PrelaunchEmailSequence])
def read_campaign_email_sequences(
    *,
    db: Session = Depends(deps.get_db),
    campaign_id: str = Path(..., title="The ID of the campaign"),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve email sequences for a campaign.
    """
    campaign = crud.course_prelaunch_campaign.get(db, id=campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    sequences = crud.prelaunch_email_sequence.get_by_campaign(db, campaign_id=campaign_id)
    return sequences


@router.post("/campaigns/{campaign_id}/email-sequences", response_model=schemas.PrelaunchEmailSequence)
def create_email_sequence(
    *,
    db: Session = Depends(deps.get_db),
    campaign_id: str = Path(..., title="The ID of the campaign"),
    sequence_in: schemas.PrelaunchEmailSequenceCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new email sequence for a campaign.
    """
    campaign = crud.course_prelaunch_campaign.get(db, id=campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Ensure campaign_id in the path matches the one in the request body
    if sequence_in.campaign_id != campaign_id:
        sequence_in.campaign_id = campaign_id
    
    sequence = crud.prelaunch_email_sequence.create(db, obj_in=sequence_in)
    return sequence


@router.get("/email-sequences/{sequence_id}", response_model=schemas.PrelaunchEmailSequenceWithEmails)
def read_email_sequence(
    *,
    db: Session = Depends(deps.get_db),
    sequence_id: str = Path(..., title="The ID of the sequence to get"),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get email sequence by ID with all emails.
    """
    sequence = crud.prelaunch_email_sequence.get_with_emails(db, sequence_id=sequence_id)
    if not sequence:
        raise HTTPException(status_code=404, detail="Email sequence not found")
    return sequence


@router.put("/email-sequences/{sequence_id}", response_model=schemas.PrelaunchEmailSequence)
def update_email_sequence(
    *,
    db: Session = Depends(deps.get_db),
    sequence_id: str = Path(..., title="The ID of the sequence to update"),
    sequence_in: schemas.PrelaunchEmailSequenceUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update an email sequence.
    """
    sequence = crud.prelaunch_email_sequence.get(db, id=sequence_id)
    if not sequence:
        raise HTTPException(status_code=404, detail="Email sequence not found")
    
    sequence = crud.prelaunch_email_sequence.update(db, db_obj=sequence, obj_in=sequence_in)
    return sequence


@router.delete("/email-sequences/{sequence_id}", response_model=schemas.PrelaunchEmailSequence)
def delete_email_sequence(
    *,
    db: Session = Depends(deps.get_db),
    sequence_id: str = Path(..., title="The ID of the sequence to delete"),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete an email sequence.
    """
    sequence = crud.prelaunch_email_sequence.get(db, id=sequence_id)
    if not sequence:
        raise HTTPException(status_code=404, detail="Email sequence not found")
    
    # Check if sequence has emails
    emails = crud.prelaunch_email.get_by_sequence(db, sequence_id=sequence_id)
    if emails:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete sequence with emails. Delete emails first.",
        )
    
    sequence = crud.prelaunch_email_sequence.remove(db, id=sequence_id)
    return sequence


# PrelaunchEmail endpoints
@router.get("/email-sequences/{sequence_id}/emails", response_model=List[schemas.PrelaunchEmail])
def read_sequence_emails(
    *,
    db: Session = Depends(deps.get_db),
    sequence_id: str = Path(..., title="The ID of the sequence"),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve emails for a sequence.
    """
    sequence = crud.prelaunch_email_sequence.get(db, id=sequence_id)
    if not sequence:
        raise HTTPException(status_code=404, detail="Email sequence not found")
    
    emails = crud.prelaunch_email.get_by_sequence(db, sequence_id=sequence_id)
    return emails


@router.post("/email-sequences/{sequence_id}/emails", response_model=schemas.PrelaunchEmail)
def create_sequence_email(
    *,
    db: Session = Depends(deps.get_db),
    sequence_id: str = Path(..., title="The ID of the sequence"),
    email_in: schemas.PrelaunchEmailCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new email for a sequence.
    """
    sequence = crud.prelaunch_email_sequence.get(db, id=sequence_id)
    if not sequence:
        raise HTTPException(status_code=404, detail="Email sequence not found")
    
    # Ensure sequence_id in the path matches the one in the request body
    if email_in.sequence_id != sequence_id:
        email_in.sequence_id = sequence_id
    
    email = crud.prelaunch_email.create(db, obj_in=email_in)
    return email


@router.get("/emails/{email_id}", response_model=schemas.PrelaunchEmail)
def read_sequence_email(
    *,
    db: Session = Depends(deps.get_db),
    email_id: str = Path(..., title="The ID of the email to get"),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get sequence email by ID.
    """
    email = crud.prelaunch_email.get(db, id=email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    return email


@router.put("/emails/{email_id}", response_model=schemas.PrelaunchEmail)
def update_sequence_email(
    *,
    db: Session = Depends(deps.get_db),
    email_id: str = Path(..., title="The ID of the email to update"),
    email_in: schemas.PrelaunchEmailUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a sequence email.
    """
    email = crud.prelaunch_email.get(db, id=email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    
    email = crud.prelaunch_email.update(db, db_obj=email, obj_in=email_in)
    return email


@router.delete("/emails/{email_id}", response_model=schemas.PrelaunchEmail)
def delete_sequence_email(
    *,
    db: Session = Depends(deps.get_db),
    email_id: str = Path(..., title="The ID of the email to delete"),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a sequence email.
    """
    email = crud.prelaunch_email.get(db, id=email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    
    email = crud.prelaunch_email.remove(db, id=email_id)
    return email


@router.post("/emails/{email_id}/stats", response_model=schemas.PrelaunchEmail)
def update_email_statistics(
    *,
    db: Session = Depends(deps.get_db),
    email_id: str = Path(..., title="The ID of the email"),
    sent: int = Body(0),
    opened: int = Body(0),
    clicked: int = Body(0),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update email statistics.
    """
    email = crud.prelaunch_email.update_statistics(
        db, email_id=email_id, sent=sent, opened=opened, clicked=clicked
    )
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    return email
