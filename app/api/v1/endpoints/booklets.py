from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Booklet])
def read_booklets(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve booklets.
    """
    booklets = crud.booklet.get_multi(db, skip=skip, limit=limit)
    return booklets


@router.post("/", response_model=schemas.Booklet)
def create_booklet(
    *,
    db: Session = Depends(deps.get_db),
    booklet_in: schemas.BookletCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new booklet.
    """
    booklet = crud.booklet.get_by_slug(db, slug=booklet_in.slug)
    if booklet:
        raise HTTPException(
            status_code=400,
            detail="A booklet with this slug already exists",
        )
    booklet = crud.booklet.create(db, obj_in=booklet_in)
    return booklet


@router.get("/{slug}", response_model=schemas.BookletWithDetails)
def read_booklet_by_slug(
    *,
    db: Session = Depends(deps.get_db),
    slug: str,
) -> Any:
    """
    Get booklet by slug with details.
    """
    booklet = crud.booklet.get_by_slug(db, slug=slug)
    if not booklet:
        raise HTTPException(status_code=404, detail="Booklet not found")
    
    # Get author, chapters, and updates
    author = crud.author.get(db, id=booklet.author_id)
    chapters = crud.booklet_chapter.get_multi_by_booklet(db, booklet_id=booklet.id)
    updates = crud.booklet_update.get_multi_by_booklet(db, booklet_id=booklet.id)
    
    # Combine into response
    result = {
        **booklet.__dict__,
        "author": author,
        "chapters": chapters,
        "updates": updates
    }
    
    return result


@router.put("/{booklet_id}", response_model=schemas.Booklet)
def update_booklet(
    *,
    db: Session = Depends(deps.get_db),
    booklet_id: str,
    booklet_in: schemas.BookletUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a booklet.
    """
    booklet = crud.booklet.get(db, id=booklet_id)
    if not booklet:
        raise HTTPException(status_code=404, detail="Booklet not found")
    booklet = crud.booklet.update(db, db_obj=booklet, obj_in=booklet_in)
    return booklet


@router.delete("/{booklet_id}", response_model=schemas.Booklet)
def delete_booklet(
    *,
    db: Session = Depends(deps.get_db),
    booklet_id: str,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a booklet.
    """
    booklet = crud.booklet.get(db, id=booklet_id)
    if not booklet:
        raise HTTPException(status_code=404, detail="Booklet not found")
    booklet = crud.booklet.remove(db, id=booklet_id)
    return booklet


# Booklet Chapter endpoints
@router.get("/{booklet_id}/chapters", response_model=List[schemas.BookletChapter])
def read_booklet_chapters(
    *,
    db: Session = Depends(deps.get_db),
    booklet_id: str,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve chapters for a booklet.
    """
    booklet = crud.booklet.get(db, id=booklet_id)
    if not booklet:
        raise HTTPException(status_code=404, detail="Booklet not found")
    chapters = crud.booklet_chapter.get_multi_by_booklet(
        db, booklet_id=booklet_id, skip=skip, limit=limit
    )
    return chapters


@router.post("/{booklet_id}/chapters", response_model=schemas.BookletChapter)
def create_booklet_chapter(
    *,
    db: Session = Depends(deps.get_db),
    booklet_id: str,
    chapter_in: schemas.BookletChapterCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new chapter for a booklet.
    """
    booklet = crud.booklet.get(db, id=booklet_id)
    if not booklet:
        raise HTTPException(status_code=404, detail="Booklet not found")
    chapter = crud.booklet_chapter.create(db, obj_in=chapter_in)
    return chapter


@router.put("/chapters/{chapter_id}", response_model=schemas.BookletChapter)
def update_booklet_chapter(
    *,
    db: Session = Depends(deps.get_db),
    chapter_id: str,
    chapter_in: schemas.BookletChapterUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a booklet chapter.
    """
    chapter = crud.booklet_chapter.get(db, id=chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    chapter = crud.booklet_chapter.update(db, db_obj=chapter, obj_in=chapter_in)
    return chapter


@router.delete("/chapters/{chapter_id}", response_model=schemas.BookletChapter)
def delete_booklet_chapter(
    *,
    db: Session = Depends(deps.get_db),
    chapter_id: str,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a booklet chapter.
    """
    chapter = crud.booklet_chapter.get(db, id=chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    chapter = crud.booklet_chapter.remove(db, id=chapter_id)
    return chapter


# Booklet Update endpoints
@router.get("/{booklet_id}/updates", response_model=List[schemas.BookletUpdateSchema])
def read_booklet_updates(
    *,
    db: Session = Depends(deps.get_db),
    booklet_id: str,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve updates for a booklet.
    """
    booklet = crud.booklet.get(db, id=booklet_id)
    if not booklet:
        raise HTTPException(status_code=404, detail="Booklet not found")
    updates = crud.booklet_update.get_multi_by_booklet(
        db, booklet_id=booklet_id, skip=skip, limit=limit
    )
    return updates


@router.post("/{booklet_id}/updates", response_model=schemas.BookletUpdateSchema)
def create_booklet_update(
    *,
    db: Session = Depends(deps.get_db),
    booklet_id: str,
    update_in: schemas.BookletUpdateCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new update for a booklet.
    """
    booklet = crud.booklet.get(db, id=booklet_id)
    if not booklet:
        raise HTTPException(status_code=404, detail="Booklet not found")
    update = crud.booklet_update.create(db, obj_in=update_in)
    return update


@router.put("/updates/{update_id}", response_model=schemas.BookletUpdateSchema)
def update_booklet_update(
    *,
    db: Session = Depends(deps.get_db),
    update_id: str,
    update_in: schemas.BookletUpdateUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a booklet update.
    """
    update = crud.booklet_update.get(db, id=update_id)
    if not update:
        raise HTTPException(status_code=404, detail="Update not found")
    update = crud.booklet_update.update(db, db_obj=update, obj_in=update_in)
    return update


@router.delete("/updates/{update_id}", response_model=schemas.BookletUpdateSchema)
def delete_booklet_update(
    *,
    db: Session = Depends(deps.get_db),
    update_id: str,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a booklet update.
    """
    update = crud.booklet_update.get(db, id=update_id)
    if not update:
        raise HTTPException(status_code=404, detail="Update not found")
    update = crud.booklet_update.remove(db, id=update_id)
    return update
