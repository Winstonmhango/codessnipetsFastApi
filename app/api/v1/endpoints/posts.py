from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.PostList])
def read_posts(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve posts.
    """
    posts = crud.post.get_multi(db, skip=skip, limit=limit)
    return posts


@router.post("/", response_model=schemas.Post)
def create_post(
    *,
    db: Session = Depends(deps.get_db),
    post_in: schemas.PostCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new post.
    """
    post = crud.post.get_by_slug(db, slug=post_in.slug)
    if post:
        raise HTTPException(
            status_code=400,
            detail="A post with this slug already exists",
        )
    post = crud.post.create(db, obj_in=post_in)
    return post


@router.get("/{slug}", response_model=schemas.Post)
def read_post(
    *,
    db: Session = Depends(deps.get_db),
    slug: str,
) -> Any:
    """
    Get post by slug.
    """
    post = crud.post.get_by_slug(db, slug=slug)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.put("/{post_id}", response_model=schemas.Post)
def update_post(
    *,
    db: Session = Depends(deps.get_db),
    post_id: str,
    post_in: schemas.PostUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a post.
    """
    post = crud.post.get(db, id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author != current_user.id and not crud.user.is_superuser(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    post = crud.post.update(db, db_obj=post, obj_in=post_in)
    return post


@router.delete("/{post_id}", response_model=schemas.Post)
def delete_post(
    *,
    db: Session = Depends(deps.get_db),
    post_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a post.
    """
    post = crud.post.get(db, id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author != current_user.id and not crud.user.is_superuser(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    post = crud.post.remove(db, id=post_id)
    return post


@router.get("/category/{category_slug}", response_model=List[schemas.PostList])
def read_posts_by_category(
    *,
    db: Session = Depends(deps.get_db),
    category_slug: str,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve posts by category.
    """
    category = crud.category.get_by_slug(db, slug=category_slug)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    posts = crud.post.get_multi_by_category(
        db, category_id=category.id, skip=skip, limit=limit
    )
    return posts


@router.get("/author/{author_id}", response_model=List[schemas.PostList])
def read_posts_by_author(
    *,
    db: Session = Depends(deps.get_db),
    author_id: str,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve posts by author.
    """
    posts = crud.post.get_multi_by_author(
        db, author=author_id, skip=skip, limit=limit
    )
    return posts


@router.get("/related/{slug}/{category_slug}", response_model=List[schemas.PostList])
def read_related_posts(
    *,
    db: Session = Depends(deps.get_db),
    slug: str,
    category_slug: str,
    limit: int = 2,
) -> Any:
    """
    Retrieve related posts.
    """
    category = crud.category.get_by_slug(db, slug=category_slug)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    posts = crud.post.get_related_posts(
        db, current_slug=slug, category_id=category.id, limit=limit
    )
    return posts
