from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Award])
def read_awards(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve awards.
    """
    if category:
        awards = crud.award.get_by_category(db, category=category)
    else:
        awards = crud.award.get_multi(db, skip=skip, limit=limit)
    return awards


@router.post("/", response_model=schemas.Award)
def create_award(
    *,
    db: Session = Depends(deps.get_db),
    award_in: schemas.AwardCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new award.
    """
    award = crud.award.create(db, obj_in=award_in)
    return award


@router.get("/{award_id}", response_model=schemas.AwardWithDetails)
def read_award(
    *,
    db: Session = Depends(deps.get_db),
    award_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get award by ID.
    """
    award = crud.award.get_with_user_count(db, id=award_id)
    if not award:
        raise HTTPException(status_code=404, detail="Award not found")
    return award


@router.put("/{award_id}", response_model=schemas.Award)
def update_award(
    *,
    db: Session = Depends(deps.get_db),
    award_id: str,
    award_in: schemas.AwardUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update an award.
    """
    award = crud.award.get(db, id=award_id)
    if not award:
        raise HTTPException(status_code=404, detail="Award not found")

    award = crud.award.update(db, db_obj=award, obj_in=award_in)
    return award


@router.delete("/{award_id}", response_model=schemas.Award)
def delete_award(
    *,
    db: Session = Depends(deps.get_db),
    award_id: str,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete an award.
    """
    award = crud.award.get(db, id=award_id)
    if not award:
        raise HTTPException(status_code=404, detail="Award not found")

    award = crud.award.remove(db, id=award_id)
    return award


@router.get("/user/{user_id}", response_model=schemas.UserWithAwards)
def read_user_awards(
    *,
    db: Session = Depends(deps.get_db),
    user_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get all awards for a user.
    """
    # Only allow users to see their own awards or admins to see anyone's
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_awards = crud.user_award.get_by_user(db, user_id=user_id)

    return {
        "id": user.id,
        "username": user.username,
        "awards": user_awards
    }


@router.post("/user/award", response_model=schemas.UserAward)
def award_user(
    *,
    db: Session = Depends(deps.get_db),
    user_award_in: schemas.UserAwardCreate,
    user_id: str,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Award a user (admin only).
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    award = crud.award.get(db, id=user_award_in.award_id)
    if not award:
        raise HTTPException(status_code=404, detail="Award not found")

    user_award = crud.user_award.create_with_user(
        db, obj_in=user_award_in, user_id=user_id
    )

    # Update user's points
    user.total_points += award.points
    db.add(user)
    db.commit()

    return user_award


@router.post("/me/check", response_model=List[schemas.UserAward])
def check_user_awards(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Check and award any new awards the user has earned.
    """
    # Get all awards
    all_awards = crud.award.get_multi(db)
    new_awards = []

    # Check each award's requirements
    for award in all_awards:
        # Skip awards the user already has
        if crud.user_award.check_user_has_award(db, user_id=current_user.id, award_id=award.id):
            continue

        # Check requirements (simplified example)
        requirements = award.requirements or {}

        # Check level requirement
        if "min_level" in requirements and current_user.level >= requirements["min_level"]:
            user_award = crud.user_award.create_with_user(
                db,
                obj_in=schemas.UserAwardCreate(
                    award_id=award.id,
                    award_metadata={"earned_by": "level_up"}
                ),
                user_id=current_user.id
            )
            new_awards.append(user_award)

            # Update user's points
            current_user.total_points += award.points
            db.add(current_user)

        # Check points requirement
        elif "min_points" in requirements and current_user.total_points >= requirements["min_points"]:
            user_award = crud.user_award.create_with_user(
                db,
                obj_in=schemas.UserAwardCreate(
                    award_id=award.id,
                    award_metadata={"earned_by": "points_milestone"}
                ),
                user_id=current_user.id
            )
            new_awards.append(user_award)

            # Update user's points
            current_user.total_points += award.points
            db.add(current_user)

    # Commit any changes
    if new_awards:
        db.commit()

    return new_awards
