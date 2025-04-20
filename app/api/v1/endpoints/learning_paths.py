from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.LearningPath])
def read_learning_paths(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve learning paths.
    """
    learning_paths = crud.learning_path.get_multi(db, skip=skip, limit=limit)
    return learning_paths


@router.post("/", response_model=schemas.LearningPath)
def create_learning_path(
    *,
    db: Session = Depends(deps.get_db),
    learning_path_in: schemas.LearningPathCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new learning path.
    """
    learning_path = crud.learning_path.get_by_slug(db, slug=learning_path_in.slug)
    if learning_path:
        raise HTTPException(
            status_code=400,
            detail="A learning path with this slug already exists",
        )
    learning_path = crud.learning_path.create(db, obj_in=learning_path_in)
    return learning_path


@router.get("/featured", response_model=List[schemas.LearningPath])
def read_featured_learning_paths(
    db: Session = Depends(deps.get_db),
    limit: int = 3,
) -> Any:
    """
    Retrieve featured learning paths.
    """
    learning_paths = crud.learning_path.get_featured(db, limit=limit)
    return learning_paths


@router.get("/tag/{tag}", response_model=List[schemas.LearningPath])
def read_learning_paths_by_tag(
    *,
    db: Session = Depends(deps.get_db),
    tag: str,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve learning paths by tag.
    """
    learning_paths = crud.learning_path.get_by_tag(db, tag=tag, skip=skip, limit=limit)
    return learning_paths


@router.get("/{slug}", response_model=schemas.LearningPathWithDetails)
def read_learning_path_by_slug(
    *,
    db: Session = Depends(deps.get_db),
    slug: str,
) -> Any:
    """
    Get learning path by slug with details.
    """
    learning_path = crud.learning_path.get_by_slug(db, slug=slug)
    if not learning_path:
        raise HTTPException(status_code=404, detail="Learning path not found")
    
    # Get modules and resources
    modules = crud.learning_path_module.get_multi_by_learning_path(db, learning_path_id=learning_path.id)
    resources = crud.learning_path_resource.get_multi_by_learning_path(db, learning_path_id=learning_path.id)
    
    # Get content items for each module
    modules_with_items = []
    for module in modules:
        content_items = crud.learning_path_content_item.get_multi_by_module(db, module_id=module.id)
        module_dict = {
            **module.__dict__,
            "content_items": content_items
        }
        modules_with_items.append(module_dict)
    
    # Combine into response
    result = {
        **learning_path.__dict__,
        "modules": modules_with_items,
        "resources": resources
    }
    
    return result


@router.put("/{learning_path_id}", response_model=schemas.LearningPath)
def update_learning_path(
    *,
    db: Session = Depends(deps.get_db),
    learning_path_id: str,
    learning_path_in: schemas.LearningPathUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a learning path.
    """
    learning_path = crud.learning_path.get(db, id=learning_path_id)
    if not learning_path:
        raise HTTPException(status_code=404, detail="Learning path not found")
    learning_path = crud.learning_path.update(db, db_obj=learning_path, obj_in=learning_path_in)
    return learning_path


@router.delete("/{learning_path_id}", response_model=schemas.LearningPath)
def delete_learning_path(
    *,
    db: Session = Depends(deps.get_db),
    learning_path_id: str,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a learning path.
    """
    learning_path = crud.learning_path.get(db, id=learning_path_id)
    if not learning_path:
        raise HTTPException(status_code=404, detail="Learning path not found")
    learning_path = crud.learning_path.remove(db, id=learning_path_id)
    return learning_path


@router.get("/related/{learning_path_id}", response_model=List[schemas.LearningPath])
def read_related_learning_paths(
    *,
    db: Session = Depends(deps.get_db),
    learning_path_id: str,
    limit: int = 3,
) -> Any:
    """
    Retrieve related learning paths.
    """
    learning_paths = crud.learning_path.get_related(db, current_id=learning_path_id, limit=limit)
    return learning_paths


# Module endpoints
@router.post("/{learning_path_id}/modules", response_model=schemas.LearningPathModule)
def create_module(
    *,
    db: Session = Depends(deps.get_db),
    learning_path_id: str,
    module_in: schemas.LearningPathModuleCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new module for a learning path.
    """
    learning_path = crud.learning_path.get(db, id=learning_path_id)
    if not learning_path:
        raise HTTPException(status_code=404, detail="Learning path not found")
    module = crud.learning_path_module.create(db, obj_in=module_in)
    return module


@router.put("/modules/{module_id}", response_model=schemas.LearningPathModule)
def update_module(
    *,
    db: Session = Depends(deps.get_db),
    module_id: str,
    module_in: schemas.LearningPathModuleUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a module.
    """
    module = crud.learning_path_module.get(db, id=module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    module = crud.learning_path_module.update(db, db_obj=module, obj_in=module_in)
    return module


@router.delete("/modules/{module_id}", response_model=schemas.LearningPathModule)
def delete_module(
    *,
    db: Session = Depends(deps.get_db),
    module_id: str,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a module.
    """
    module = crud.learning_path_module.get(db, id=module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    module = crud.learning_path_module.remove(db, id=module_id)
    return module


# Content Item endpoints
@router.post("/modules/{module_id}/items", response_model=schemas.LearningPathContentItem)
def create_content_item(
    *,
    db: Session = Depends(deps.get_db),
    module_id: str,
    item_in: schemas.LearningPathContentItemCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new content item for a module.
    """
    module = crud.learning_path_module.get(db, id=module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    item = crud.learning_path_content_item.create(db, obj_in=item_in)
    return item


@router.put("/items/{item_id}", response_model=schemas.LearningPathContentItem)
def update_content_item(
    *,
    db: Session = Depends(deps.get_db),
    item_id: str,
    item_in: schemas.LearningPathContentItemUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a content item.
    """
    item = crud.learning_path_content_item.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Content item not found")
    item = crud.learning_path_content_item.update(db, db_obj=item, obj_in=item_in)
    return item


@router.delete("/items/{item_id}", response_model=schemas.LearningPathContentItem)
def delete_content_item(
    *,
    db: Session = Depends(deps.get_db),
    item_id: str,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a content item.
    """
    item = crud.learning_path_content_item.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Content item not found")
    item = crud.learning_path_content_item.remove(db, id=item_id)
    return item


# Resource endpoints
@router.post("/{learning_path_id}/resources", response_model=schemas.LearningPathResource)
def create_resource(
    *,
    db: Session = Depends(deps.get_db),
    learning_path_id: str,
    resource_in: schemas.LearningPathResourceCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new resource for a learning path.
    """
    learning_path = crud.learning_path.get(db, id=learning_path_id)
    if not learning_path:
        raise HTTPException(status_code=404, detail="Learning path not found")
    resource = crud.learning_path_resource.create(db, obj_in=resource_in)
    return resource


@router.put("/resources/{resource_id}", response_model=schemas.LearningPathResource)
def update_resource(
    *,
    db: Session = Depends(deps.get_db),
    resource_id: str,
    resource_in: schemas.LearningPathResourceUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a resource.
    """
    resource = crud.learning_path_resource.get(db, id=resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    resource = crud.learning_path_resource.update(db, db_obj=resource, obj_in=resource_in)
    return resource


@router.delete("/resources/{resource_id}", response_model=schemas.LearningPathResource)
def delete_resource(
    *,
    db: Session = Depends(deps.get_db),
    resource_id: str,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a resource.
    """
    resource = crud.learning_path_resource.get(db, id=resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    resource = crud.learning_path_resource.remove(db, id=resource_id)
    return resource
