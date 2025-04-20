from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


# Author endpoints
@router.get("/authors/", response_model=List[schemas.Author])
def read_authors(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve authors.
    """
    authors = crud.author.get_multi(db, skip=skip, limit=limit)
    return authors


@router.post("/authors/", response_model=schemas.Author)
def create_author(
    *,
    db: Session = Depends(deps.get_db),
    author_in: schemas.AuthorCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new author.
    """
    author = crud.author.create(db, obj_in=author_in)
    return author


@router.get("/authors/{author_id}", response_model=schemas.Author)
def read_author(
    *,
    db: Session = Depends(deps.get_db),
    author_id: str,
) -> Any:
    """
    Get author by ID.
    """
    author = crud.author.get(db, id=author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return author


@router.put("/authors/{author_id}", response_model=schemas.Author)
def update_author(
    *,
    db: Session = Depends(deps.get_db),
    author_id: str,
    author_in: schemas.AuthorUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update an author.
    """
    author = crud.author.get(db, id=author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    author = crud.author.update(db, db_obj=author, obj_in=author_in)
    return author


# Series endpoints
@router.get("/", response_model=List[schemas.Series])
def read_series(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve series.
    """
    series = crud.series.get_multi(db, skip=skip, limit=limit)
    return series


@router.post("/", response_model=schemas.Series)
def create_series(
    *,
    db: Session = Depends(deps.get_db),
    series_in: schemas.SeriesCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new series.
    """
    series = crud.series.get_by_slug(db, slug=series_in.slug)
    if series:
        raise HTTPException(
            status_code=400,
            detail="A series with this slug already exists",
        )
    series = crud.series.create(db, obj_in=series_in)
    return series


@router.get("/{slug}", response_model=schemas.SeriesWithDetails)
def read_series_by_slug(
    *,
    db: Session = Depends(deps.get_db),
    slug: str,
) -> Any:
    """
    Get series by slug with details.
    """
    series = crud.series.get_by_slug(db, slug=slug)
    if not series:
        raise HTTPException(status_code=404, detail="Series not found")
    
    # Get author and articles
    author = crud.author.get(db, id=series.author_id)
    articles = crud.series_article.get_multi_by_series(db, series_id=series.id)
    
    # Combine into response
    result = {
        **series.__dict__,
        "author": author,
        "articles": articles
    }
    
    return result


@router.put("/{series_id}", response_model=schemas.Series)
def update_series(
    *,
    db: Session = Depends(deps.get_db),
    series_id: str,
    series_in: schemas.SeriesUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a series.
    """
    series = crud.series.get(db, id=series_id)
    if not series:
        raise HTTPException(status_code=404, detail="Series not found")
    series = crud.series.update(db, db_obj=series, obj_in=series_in)
    return series


@router.delete("/{series_id}", response_model=schemas.Series)
def delete_series(
    *,
    db: Session = Depends(deps.get_db),
    series_id: str,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a series.
    """
    series = crud.series.get(db, id=series_id)
    if not series:
        raise HTTPException(status_code=404, detail="Series not found")
    series = crud.series.remove(db, id=series_id)
    return series


@router.get("/related/{series_id}", response_model=List[schemas.Series])
def read_related_series(
    *,
    db: Session = Depends(deps.get_db),
    series_id: str,
    limit: int = 3,
) -> Any:
    """
    Retrieve related series.
    """
    series = crud.series.get_related_series(db, current_id=series_id, limit=limit)
    return series


# Series Article endpoints
@router.get("/{series_id}/articles", response_model=List[schemas.SeriesArticle])
def read_series_articles(
    *,
    db: Session = Depends(deps.get_db),
    series_id: str,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve articles for a series.
    """
    series = crud.series.get(db, id=series_id)
    if not series:
        raise HTTPException(status_code=404, detail="Series not found")
    articles = crud.series_article.get_multi_by_series(
        db, series_id=series_id, skip=skip, limit=limit
    )
    return articles


@router.post("/{series_id}/articles", response_model=schemas.SeriesArticle)
def create_series_article(
    *,
    db: Session = Depends(deps.get_db),
    series_id: str,
    article_in: schemas.SeriesArticleCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new article for a series.
    """
    series = crud.series.get(db, id=series_id)
    if not series:
        raise HTTPException(status_code=404, detail="Series not found")
    article = crud.series_article.create(db, obj_in=article_in)
    return article


@router.put("/articles/{article_id}", response_model=schemas.SeriesArticle)
def update_series_article(
    *,
    db: Session = Depends(deps.get_db),
    article_id: str,
    article_in: schemas.SeriesArticleUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a series article.
    """
    article = crud.series_article.get(db, id=article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    article = crud.series_article.update(db, db_obj=article, obj_in=article_in)
    return article


@router.delete("/articles/{article_id}", response_model=schemas.SeriesArticle)
def delete_series_article(
    *,
    db: Session = Depends(deps.get_db),
    article_id: str,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a series article.
    """
    article = crud.series_article.get(db, id=article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    article = crud.series_article.remove(db, id=article_id)
    return article
