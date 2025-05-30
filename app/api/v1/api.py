from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth, users, categories, posts, series, booklets, learning_paths,
    quizzes, awards, courses, marketing, prelaunch
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(posts.router, prefix="/posts", tags=["posts"])
api_router.include_router(series.router, prefix="/series", tags=["series"])
api_router.include_router(booklets.router, prefix="/booklets", tags=["booklets"])
api_router.include_router(learning_paths.router, prefix="/learning-paths", tags=["learning paths"])
api_router.include_router(quizzes.router, prefix="/quizzes", tags=["quizzes"])
api_router.include_router(awards.router, prefix="/awards", tags=["awards"])
api_router.include_router(courses.router, prefix="/courses", tags=["courses"])
api_router.include_router(marketing.router, prefix="/marketing", tags=["marketing"])
api_router.include_router(prelaunch.router, prefix="/prelaunch", tags=["prelaunch"])
