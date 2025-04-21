from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


# Course Category endpoints
@router.get("/categories/", response_model=List[schemas.CourseCategory])
def read_course_categories(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    parent_id: Optional[str] = None,
) -> Any:
    """
    Retrieve course categories.
    """
    if parent_id:
        categories = crud.course_category.get_subcategories(db, parent_id=parent_id)
    else:
        categories = crud.course_category.get_root_categories(db, skip=skip, limit=limit)
    return categories


@router.post("/categories/", response_model=schemas.CourseCategory)
def create_course_category(
    *,
    db: Session = Depends(deps.get_db),
    category_in: schemas.CourseCategoryCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new course category.
    """
    # Check if slug already exists
    category = crud.course_category.get_by_slug(db, slug=category_in.slug)
    if category:
        raise HTTPException(
            status_code=400,
            detail="Category with this slug already exists",
        )
    category = crud.course_category.create(db, obj_in=category_in)
    return category


@router.get("/categories/{category_id}", response_model=schemas.CourseCategory)
def read_course_category(
    *,
    db: Session = Depends(deps.get_db),
    category_id: str = Path(..., title="The ID of the category to get"),
) -> Any:
    """
    Get course category by ID.
    """
    category = crud.course_category.get(db, id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put("/categories/{category_id}", response_model=schemas.CourseCategory)
def update_course_category(
    *,
    db: Session = Depends(deps.get_db),
    category_id: str = Path(..., title="The ID of the category to update"),
    category_in: schemas.CourseCategoryUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a course category.
    """
    category = crud.course_category.get(db, id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Check if slug already exists (if updating slug)
    if category_in.slug and category_in.slug != category.slug:
        existing = crud.course_category.get_by_slug(db, slug=category_in.slug)
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Category with this slug already exists",
            )

    category = crud.course_category.update(db, db_obj=category, obj_in=category_in)
    return category


@router.delete("/categories/{category_id}", response_model=schemas.CourseCategory)
def delete_course_category(
    *,
    db: Session = Depends(deps.get_db),
    category_id: str = Path(..., title="The ID of the category to delete"),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a course category.
    """
    category = crud.course_category.get(db, id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Check if category has subcategories
    subcategories = crud.course_category.get_subcategories(db, parent_id=category_id)
    if subcategories:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete category with subcategories",
        )

    # Check if category has courses
    courses = crud.course.get_by_category(db, category_id=category_id)
    if courses:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete category with courses",
        )

    category = crud.course_category.remove(db, id=category_id)
    return category


# Course endpoints
@router.get("/", response_model=List[schemas.Course])
def read_courses(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[str] = None,
    author_id: Optional[str] = None,
    search: Optional[str] = None,
    featured: Optional[bool] = None,
) -> Any:
    """
    Retrieve courses.
    """
    if search:
        courses = crud.course.search(db, query=search, skip=skip, limit=limit)
    elif category_id:
        courses = crud.course.get_by_category(db, category_id=category_id, skip=skip, limit=limit)
    elif author_id:
        courses = crud.course.get_by_author(db, author_id=author_id, skip=skip, limit=limit)
    elif featured:
        courses = crud.course.get_featured(db, limit=limit)
    else:
        courses = crud.course.get_multi(db, skip=skip, limit=limit)
    return courses


@router.post("/", response_model=schemas.Course)
def create_course(
    *,
    db: Session = Depends(deps.get_db),
    course_in: schemas.CourseCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new course.
    """
    # Check if slug already exists
    course = crud.course.get_by_slug(db, slug=course_in.slug)
    if course:
        raise HTTPException(
            status_code=400,
            detail="Course with this slug already exists",
        )

    # Check if user is superuser or the author
    if not current_user.is_superuser and course_in.author_id != current_user.id:
        # Check if user is the author
        author = crud.author.get(db, id=course_in.author_id)
        if not author or author.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions to create course for this author",
            )

    course = crud.course.create(db, obj_in=course_in)
    return course


@router.get("/{course_id}", response_model=schemas.CourseWithDetails)
def read_course(
    *,
    db: Session = Depends(deps.get_db),
    course_id: str = Path(..., title="The ID of the course to get"),
    current_user: Optional[models.User] = Depends(deps.get_current_user_optional),
) -> Any:
    """
    Get course by ID.
    """
    course = crud.course.get(db, id=course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Get modules, topics, and lessons
    modules = crud.course_module.get_by_course(db, course_id=course_id)

    # Get author and category details
    author = crud.author.get(db, id=course.author_id) if course.author_id else None
    category = crud.course_category.get(db, id=course.category_id) if course.category_id else None

    # Get enrollment if user is logged in
    enrollment = None
    if current_user:
        enrollment = crud.course_enrollment.get_by_user_and_course(
            db, user_id=current_user.id, course_id=course_id
        )

    # Build response
    result = course.__dict__.copy()
    result["modules"] = []

    for module in modules:
        module_dict = module.__dict__.copy()
        module_dict["topics"] = []

        topics = crud.course_topic.get_by_module(db, module_id=module.id)
        for topic in topics:
            topic_dict = topic.__dict__.copy()
            topic_dict["lessons"] = []

            lessons = crud.topic_lesson.get_by_topic(db, topic_id=topic.id)
            for lesson in lessons:
                lesson_dict = lesson.__dict__.copy()

                # Get quiz if exists
                quiz = db.query(models.Quiz).filter(
                    models.Quiz.content_type == "lesson",
                    models.Quiz.content_id == lesson.id
                ).first()

                lesson_dict["quiz"] = quiz.__dict__ if quiz else None
                topic_dict["lessons"].append(lesson_dict)

            module_dict["topics"].append(topic_dict)

        result["modules"].append(module_dict)

    result["author"] = author.__dict__ if author else None
    result["category"] = category.__dict__ if category else None
    result["enrollment"] = enrollment.__dict__ if enrollment else None

    return result


@router.put("/{course_id}", response_model=schemas.Course)
def update_course(
    *,
    db: Session = Depends(deps.get_db),
    course_id: str = Path(..., title="The ID of the course to update"),
    course_in: schemas.CourseUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a course.
    """
    course = crud.course.get(db, id=course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Check if user is superuser or the author
    if not current_user.is_superuser:
        # Check if user is the author
        author = crud.author.get(db, id=course.author_id)
        if not author or author.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions to update this course",
            )

    # Check if slug already exists (if updating slug)
    if course_in.slug and course_in.slug != course.slug:
        existing = crud.course.get_by_slug(db, slug=course_in.slug)
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Course with this slug already exists",
            )

    course = crud.course.update(db, db_obj=course, obj_in=course_in)
    return course


@router.delete("/{course_id}", response_model=schemas.Course)
def delete_course(
    *,
    db: Session = Depends(deps.get_db),
    course_id: str = Path(..., title="The ID of the course to delete"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a course.
    """
    course = crud.course.get(db, id=course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Check if user is superuser or the author
    if not current_user.is_superuser:
        # Check if user is the author
        author = crud.author.get(db, id=course.author_id)
        if not author or author.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions to delete this course",
            )

    course = crud.course.remove(db, id=course_id)
    return course


@router.post("/{course_id}/publish", response_model=schemas.Course)
def publish_course(
    *,
    db: Session = Depends(deps.get_db),
    course_id: str = Path(..., title="The ID of the course to publish"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Publish a course.
    """
    course = crud.course.get(db, id=course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Check if user is superuser or the author
    if not current_user.is_superuser:
        # Check if user is the author
        author = crud.author.get(db, id=course.author_id)
        if not author or author.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions to publish this course",
            )

    course = crud.course.publish(db, db_obj=course)
    return course


@router.post("/{course_id}/unpublish", response_model=schemas.Course)
def unpublish_course(
    *,
    db: Session = Depends(deps.get_db),
    course_id: str = Path(..., title="The ID of the course to unpublish"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Unpublish a course.
    """
    course = crud.course.get(db, id=course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Check if user is superuser or the author
    if not current_user.is_superuser:
        # Check if user is the author
        author = crud.author.get(db, id=course.author_id)
        if not author or author.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions to unpublish this course",
            )

    course = crud.course.unpublish(db, db_obj=course)
    return course


@router.post("/{course_id}/learning-paths/{learning_path_id}", response_model=schemas.Course)
def add_course_to_learning_path(
    *,
    db: Session = Depends(deps.get_db),
    course_id: str = Path(..., title="The ID of the course"),
    learning_path_id: str = Path(..., title="The ID of the learning path"),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Add a course to a learning path.
    """
    course = crud.course.get(db, id=course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    learning_path = crud.learning_path.get(db, id=learning_path_id)
    if not learning_path:
        raise HTTPException(status_code=404, detail="Learning path not found")

    course = crud.course.add_to_learning_path(db, course_id=course_id, learning_path_id=learning_path_id)
    return course


@router.delete("/{course_id}/learning-paths/{learning_path_id}", response_model=schemas.Course)
def remove_course_from_learning_path(
    *,
    db: Session = Depends(deps.get_db),
    course_id: str = Path(..., title="The ID of the course"),
    learning_path_id: str = Path(..., title="The ID of the learning path"),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Remove a course from a learning path.
    """
    course = crud.course.get(db, id=course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    learning_path = crud.learning_path.get(db, id=learning_path_id)
    if not learning_path:
        raise HTTPException(status_code=404, detail="Learning path not found")

    course = crud.course.remove_from_learning_path(db, course_id=course_id, learning_path_id=learning_path_id)
    return course


# Course Module endpoints
@router.get("/{course_id}/modules", response_model=List[schemas.CourseModule])
def read_course_modules(
    *,
    db: Session = Depends(deps.get_db),
    course_id: str = Path(..., title="The ID of the course"),
) -> Any:
    """
    Retrieve course modules.
    """
    course = crud.course.get(db, id=course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    modules = crud.course_module.get_by_course(db, course_id=course_id)
    return modules


@router.post("/{course_id}/modules", response_model=schemas.CourseModule)
def create_course_module(
    *,
    db: Session = Depends(deps.get_db),
    course_id: str = Path(..., title="The ID of the course"),
    module_in: schemas.CourseModuleCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new course module.
    """
    course = crud.course.get(db, id=course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Check if user is superuser or the author
    if not current_user.is_superuser:
        # Check if user is the author
        author = crud.author.get(db, id=course.author_id)
        if not author or author.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions to add modules to this course",
            )

    # Ensure course_id in the path matches the one in the request body
    if module_in.course_id != course_id:
        module_in.course_id = course_id

    module = crud.course_module.create(db, obj_in=module_in)
    return module


@router.get("/modules/{module_id}", response_model=schemas.CourseModuleWithTopics)
def read_course_module(
    *,
    db: Session = Depends(deps.get_db),
    module_id: str = Path(..., title="The ID of the module to get"),
) -> Any:
    """
    Get course module by ID.
    """
    module = crud.course_module.get(db, id=module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    # Get topics and lessons
    topics = crud.course_topic.get_by_module(db, module_id=module_id)

    # Build response
    result = module.__dict__.copy()
    result["topics"] = []

    for topic in topics:
        topic_dict = topic.__dict__.copy()
        topic_dict["lessons"] = []

        lessons = crud.topic_lesson.get_by_topic(db, topic_id=topic.id)
        for lesson in lessons:
            lesson_dict = lesson.__dict__.copy()

            # Get quiz if exists
            quiz = db.query(models.Quiz).filter(
                models.Quiz.content_type == "lesson",
                models.Quiz.content_id == lesson.id
            ).first()

            lesson_dict["quiz"] = quiz.__dict__ if quiz else None
            topic_dict["lessons"].append(lesson_dict)

        result["topics"].append(topic_dict)

    return result


@router.put("/modules/{module_id}", response_model=schemas.CourseModule)
def update_course_module(
    *,
    db: Session = Depends(deps.get_db),
    module_id: str = Path(..., title="The ID of the module to update"),
    module_in: schemas.CourseModuleUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a course module.
    """
    module = crud.course_module.get(db, id=module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    # Get course to check permissions
    course = crud.course.get(db, id=module.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Check if user is superuser or the author
    if not current_user.is_superuser:
        # Check if user is the author
        author = crud.author.get(db, id=course.author_id)
        if not author or author.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions to update this module",
            )

    module = crud.course_module.update(db, db_obj=module, obj_in=module_in)
    return module


@router.delete("/modules/{module_id}", response_model=schemas.CourseModule)
def delete_course_module(
    *,
    db: Session = Depends(deps.get_db),
    module_id: str = Path(..., title="The ID of the module to delete"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a course module.
    """
    module = crud.course_module.get(db, id=module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    # Get course to check permissions
    course = crud.course.get(db, id=module.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Check if user is superuser or the author
    if not current_user.is_superuser:
        # Check if user is the author
        author = crud.author.get(db, id=course.author_id)
        if not author or author.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions to delete this module",
            )

    # Check if module has topics
    topics = crud.course_topic.get_by_module(db, module_id=module_id)
    if topics:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete module with topics. Delete topics first.",
        )

    module = crud.course_module.remove(db, id=module_id)
    return module


@router.post("/modules/{module_id}/reorder", response_model=schemas.CourseModule)
def reorder_course_module(
    *,
    db: Session = Depends(deps.get_db),
    module_id: str = Path(..., title="The ID of the module to reorder"),
    new_order: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Reorder a course module.
    """
    module = crud.course_module.get(db, id=module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    # Get course to check permissions
    course = crud.course.get(db, id=module.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Check if user is superuser or the author
    if not current_user.is_superuser:
        # Check if user is the author
        author = crud.author.get(db, id=course.author_id)
        if not author or author.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions to reorder this module",
            )

    module = crud.course_module.reorder(db, module_id=module_id, new_order=new_order)
    return module


# Course Topic endpoints
@router.get("/modules/{module_id}/topics", response_model=List[schemas.CourseTopic])
def read_course_topics(
    *,
    db: Session = Depends(deps.get_db),
    module_id: str = Path(..., title="The ID of the module"),
) -> Any:
    """
    Retrieve course topics.
    """
    module = crud.course_module.get(db, id=module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    topics = crud.course_topic.get_by_module(db, module_id=module_id)
    return topics


@router.post("/modules/{module_id}/topics", response_model=schemas.CourseTopic)
def create_course_topic(
    *,
    db: Session = Depends(deps.get_db),
    module_id: str = Path(..., title="The ID of the module"),
    topic_in: schemas.CourseTopicCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new course topic.
    """
    module = crud.course_module.get(db, id=module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    # Get course to check permissions
    course = crud.course.get(db, id=module.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Check if user is superuser or the author
    if not current_user.is_superuser:
        # Check if user is the author
        author = crud.author.get(db, id=course.author_id)
        if not author or author.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions to add topics to this module",
            )

    # Ensure module_id in the path matches the one in the request body
    if topic_in.module_id != module_id:
        topic_in.module_id = module_id

    topic = crud.course_topic.create(db, obj_in=topic_in)
    return topic


@router.get("/topics/{topic_id}", response_model=schemas.CourseTopicWithLessons)
def read_course_topic(
    *,
    db: Session = Depends(deps.get_db),
    topic_id: str = Path(..., title="The ID of the topic to get"),
) -> Any:
    """
    Get course topic by ID.
    """
    topic = crud.course_topic.get(db, id=topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    # Get lessons
    lessons = crud.topic_lesson.get_by_topic(db, topic_id=topic_id)

    # Build response
    result = topic.__dict__.copy()
    result["lessons"] = []

    for lesson in lessons:
        lesson_dict = lesson.__dict__.copy()

        # Get quiz if exists
        quiz = db.query(models.Quiz).filter(
            models.Quiz.content_type == "lesson",
            models.Quiz.content_id == lesson.id
        ).first()

        lesson_dict["quiz"] = quiz.__dict__ if quiz else None
        result["lessons"].append(lesson_dict)

    return result


@router.put("/topics/{topic_id}", response_model=schemas.CourseTopic)
def update_course_topic(
    *,
    db: Session = Depends(deps.get_db),
    topic_id: str = Path(..., title="The ID of the topic to update"),
    topic_in: schemas.CourseTopicUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a course topic.
    """
    topic = crud.course_topic.get(db, id=topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    # Get module and course to check permissions
    module = crud.course_module.get(db, id=topic.module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    course = crud.course.get(db, id=module.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Check if user is superuser or the author
    if not current_user.is_superuser:
        # Check if user is the author
        author = crud.author.get(db, id=course.author_id)
        if not author or author.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions to update this topic",
            )

    topic = crud.course_topic.update(db, db_obj=topic, obj_in=topic_in)
    return topic


@router.delete("/topics/{topic_id}", response_model=schemas.CourseTopic)
def delete_course_topic(
    *,
    db: Session = Depends(deps.get_db),
    topic_id: str = Path(..., title="The ID of the topic to delete"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a course topic.
    """
    topic = crud.course_topic.get(db, id=topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    # Get module and course to check permissions
    module = crud.course_module.get(db, id=topic.module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    course = crud.course.get(db, id=module.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Check if user is superuser or the author
    if not current_user.is_superuser:
        # Check if user is the author
        author = crud.author.get(db, id=course.author_id)
        if not author or author.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions to delete this topic",
            )

    # Check if topic has lessons
    lessons = crud.topic_lesson.get_by_topic(db, topic_id=topic_id)
    if lessons:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete topic with lessons. Delete lessons first.",
        )

    topic = crud.course_topic.remove(db, id=topic_id)
    return topic


@router.post("/topics/{topic_id}/reorder", response_model=schemas.CourseTopic)
def reorder_course_topic(
    *,
    db: Session = Depends(deps.get_db),
    topic_id: str = Path(..., title="The ID of the topic to reorder"),
    new_order: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Reorder a course topic.
    """
    topic = crud.course_topic.get(db, id=topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    # Get module and course to check permissions
    module = crud.course_module.get(db, id=topic.module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    course = crud.course.get(db, id=module.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Check if user is superuser or the author
    if not current_user.is_superuser:
        # Check if user is the author
        author = crud.author.get(db, id=course.author_id)
        if not author or author.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions to reorder this topic",
            )

    topic = crud.course_topic.reorder(db, topic_id=topic_id, new_order=new_order)
    return topic


# Topic Lesson endpoints
@router.get("/topics/{topic_id}/lessons", response_model=List[schemas.TopicLesson])
def read_topic_lessons(
    *,
    db: Session = Depends(deps.get_db),
    topic_id: str = Path(..., title="The ID of the topic"),
) -> Any:
    """
    Retrieve topic lessons.
    """
    topic = crud.course_topic.get(db, id=topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    lessons = crud.topic_lesson.get_by_topic(db, topic_id=topic_id)
    return lessons


@router.post("/topics/{topic_id}/lessons", response_model=schemas.TopicLesson)
def create_topic_lesson(
    *,
    db: Session = Depends(deps.get_db),
    topic_id: str = Path(..., title="The ID of the topic"),
    lesson_in: schemas.TopicLessonCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new topic lesson.
    """
    topic = crud.course_topic.get(db, id=topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    # Get module and course to check permissions
    module = crud.course_module.get(db, id=topic.module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    course = crud.course.get(db, id=module.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Check if user is superuser or the author
    if not current_user.is_superuser:
        # Check if user is the author
        author = crud.author.get(db, id=course.author_id)
        if not author or author.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions to add lessons to this topic",
            )

    # Ensure topic_id in the path matches the one in the request body
    if lesson_in.topic_id != topic_id:
        lesson_in.topic_id = topic_id

    lesson = crud.topic_lesson.create(db, obj_in=lesson_in)
    return lesson


@router.get("/lessons/{lesson_id}", response_model=schemas.TopicLessonWithQuiz)
def read_topic_lesson(
    *,
    db: Session = Depends(deps.get_db),
    lesson_id: str = Path(..., title="The ID of the lesson to get"),
) -> Any:
    """
    Get topic lesson by ID.
    """
    lesson = crud.topic_lesson.get(db, id=lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Get quiz if exists
    quiz = db.query(models.Quiz).filter(
        models.Quiz.content_type == "lesson",
        models.Quiz.content_id == lesson.id
    ).first()

    # Build response
    result = lesson.__dict__.copy()
    result["quiz"] = quiz.__dict__ if quiz else None

    return result


@router.put("/lessons/{lesson_id}", response_model=schemas.TopicLesson)
def update_topic_lesson(
    *,
    db: Session = Depends(deps.get_db),
    lesson_id: str = Path(..., title="The ID of the lesson to update"),
    lesson_in: schemas.TopicLessonUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a topic lesson.
    """
    lesson = crud.topic_lesson.get(db, id=lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Get topic, module, and course to check permissions
    topic = crud.course_topic.get(db, id=lesson.topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    module = crud.course_module.get(db, id=topic.module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    course = crud.course.get(db, id=module.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Check if user is superuser or the author
    if not current_user.is_superuser:
        # Check if user is the author
        author = crud.author.get(db, id=course.author_id)
        if not author or author.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions to update this lesson",
            )

    lesson = crud.topic_lesson.update(db, db_obj=lesson, obj_in=lesson_in)
    return lesson


@router.delete("/lessons/{lesson_id}", response_model=schemas.TopicLesson)
def delete_topic_lesson(
    *,
    db: Session = Depends(deps.get_db),
    lesson_id: str = Path(..., title="The ID of the lesson to delete"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a topic lesson.
    """
    lesson = crud.topic_lesson.get(db, id=lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Get topic, module, and course to check permissions
    topic = crud.course_topic.get(db, id=lesson.topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    module = crud.course_module.get(db, id=topic.module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    course = crud.course.get(db, id=module.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Check if user is superuser or the author
    if not current_user.is_superuser:
        # Check if user is the author
        author = crud.author.get(db, id=course.author_id)
        if not author or author.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions to delete this lesson",
            )

    # Check if lesson has a quiz and delete it
    quiz = db.query(models.Quiz).filter(
        models.Quiz.content_type == "lesson",
        models.Quiz.content_id == lesson.id
    ).first()

    if quiz:
        crud.quiz.remove(db, id=quiz.id)

    lesson = crud.topic_lesson.remove(db, id=lesson_id)
    return lesson


@router.post("/lessons/{lesson_id}/reorder", response_model=schemas.TopicLesson)
def reorder_topic_lesson(
    *,
    db: Session = Depends(deps.get_db),
    lesson_id: str = Path(..., title="The ID of the lesson to reorder"),
    new_order: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Reorder a topic lesson.
    """
    lesson = crud.topic_lesson.get(db, id=lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Get topic, module, and course to check permissions
    topic = crud.course_topic.get(db, id=lesson.topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    module = crud.course_module.get(db, id=topic.module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    course = crud.course.get(db, id=module.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Check if user is superuser or the author
    if not current_user.is_superuser:
        # Check if user is the author
        author = crud.author.get(db, id=course.author_id)
        if not author or author.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions to reorder this lesson",
            )

    lesson = crud.topic_lesson.reorder(db, lesson_id=lesson_id, new_order=new_order)
    return lesson


@router.post("/lessons/{lesson_id}/quiz", response_model=schemas.Quiz)
def create_lesson_quiz(
    *,
    db: Session = Depends(deps.get_db),
    lesson_id: str = Path(..., title="The ID of the lesson"),
    quiz_data: dict,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create a quiz for a lesson.
    """
    lesson = crud.topic_lesson.get(db, id=lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Get topic, module, and course to check permissions
    topic = crud.course_topic.get(db, id=lesson.topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    module = crud.course_module.get(db, id=topic.module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    course = crud.course.get(db, id=module.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Check if user is superuser or the author
    if not current_user.is_superuser:
        # Check if user is the author
        author = crud.author.get(db, id=course.author_id)
        if not author or author.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions to add a quiz to this lesson",
            )

    # Check if lesson already has a quiz
    existing_quiz = db.query(models.Quiz).filter(
        models.Quiz.content_type == "lesson",
        models.Quiz.content_id == lesson.id
    ).first()

    if existing_quiz:
        raise HTTPException(
            status_code=400,
            detail="Lesson already has a quiz",
        )

    quiz = crud.topic_lesson.create_quiz(db, lesson_id=lesson_id, quiz_data=quiz_data)
    return quiz


# Course Enrollment endpoints
@router.post("/enroll/{course_id}", response_model=schemas.CourseEnrollment)
def enroll_in_course(
    *,
    db: Session = Depends(deps.get_db),
    course_id: str = Path(..., title="The ID of the course to enroll in"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Enroll in a course.
    """
    course = crud.course.get(db, id=course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Check if course is published
    if not course.is_published:
        raise HTTPException(
            status_code=400,
            detail="Cannot enroll in an unpublished course",
        )

    # Check if user is already enrolled
    existing = crud.course_enrollment.get_by_user_and_course(
        db, user_id=current_user.id, course_id=course_id
    )

    if existing:
        return existing

    # Create enrollment
    enrollment_in = schemas.CourseEnrollmentCreate(course_id=course_id)
    enrollment = crud.course_enrollment.create_with_user(
        db, obj_in=enrollment_in, user_id=current_user.id
    )

    return enrollment


@router.get("/enrollments/me", response_model=List[schemas.CourseEnrollment])
def read_my_enrollments(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user's enrollments.
    """
    enrollments = crud.course_enrollment.get_by_user(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    return enrollments


@router.get("/enrollments/{enrollment_id}", response_model=schemas.CourseEnrollment)
def read_enrollment(
    *,
    db: Session = Depends(deps.get_db),
    enrollment_id: str = Path(..., title="The ID of the enrollment to get"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get enrollment by ID.
    """
    enrollment = crud.course_enrollment.get(db, id=enrollment_id)
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    # Check if user is the owner of the enrollment or a superuser
    if enrollment.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to access this enrollment",
        )

    return enrollment


@router.post("/enrollments/{enrollment_id}/complete", response_model=schemas.CourseEnrollment)
def complete_enrollment(
    *,
    db: Session = Depends(deps.get_db),
    enrollment_id: str = Path(..., title="The ID of the enrollment to complete"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Mark an enrollment as completed.
    """
    enrollment = crud.course_enrollment.get(db, id=enrollment_id)
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    # Check if user is the owner of the enrollment or a superuser
    if enrollment.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to update this enrollment",
        )

    enrollment = crud.course_enrollment.mark_completed(db, enrollment_id=enrollment_id)

    # Award experience points and update user level
    course = crud.course.get(db, id=enrollment.course_id)
    if course:
        # Award experience points based on course level
        level_xp = {
            "beginner": 50,
            "intermediate": 100,
            "advanced": 150,
        }
        xp_gained = level_xp.get(course.level, 50)

        # Update user's experience and level
        current_user.experience += xp_gained
        current_user.total_points += int(xp_gained * 0.5)  # Half of XP as points

        # Calculate new level (simple level calculation)
        new_level = 1 + (current_user.experience // 100)  # Level up every 100 XP
        if new_level > current_user.level:
            current_user.level = new_level

        db.add(current_user)
        db.commit()

    return enrollment


# Course Progress endpoints
@router.post("/progress", response_model=schemas.CourseProgress)
def create_or_update_progress(
    *,
    db: Session = Depends(deps.get_db),
    enrollment_id: str,
    content_type: str,
    content_id: str,
    is_completed: bool = False,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create or update progress record.
    """
    # Check if enrollment exists and belongs to the user
    enrollment = crud.course_enrollment.get(db, id=enrollment_id)
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    if enrollment.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to update this progress",
        )

    # Create or update progress
    progress = crud.course_progress.create_or_update(
        db,
        enrollment_id=enrollment_id,
        content_type=content_type,
        content_id=content_id,
        is_completed=is_completed
    )

    return progress


@router.get("/progress/{enrollment_id}", response_model=List[schemas.CourseProgress])
def read_progress(
    *,
    db: Session = Depends(deps.get_db),
    enrollment_id: str = Path(..., title="The ID of the enrollment"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get progress records for an enrollment.
    """
    # Check if enrollment exists and belongs to the user
    enrollment = crud.course_enrollment.get(db, id=enrollment_id)
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    if enrollment.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to access this progress",
        )

    progress = crud.course_progress.get_by_enrollment(db, enrollment_id=enrollment_id)
    return progress
