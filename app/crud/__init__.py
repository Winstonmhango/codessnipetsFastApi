from app.crud.user import user
from app.crud.category import category
from app.crud.post import post
from app.crud.series import author, series, series_article
from app.crud.booklet import booklet, booklet_chapter, booklet_update
from app.crud.learning_path import (
    learning_path,
    learning_path_module,
    learning_path_content_item,
    learning_path_resource,
)
from app.crud.quiz import quiz, user_quiz_attempt
from app.crud.award import award, user_award
from app.crud.course import (
    course_category,
    course,
    course_module,
    course_topic,
    topic_lesson,
    course_enrollment,
    course_progress,
)
from app.crud.marketing import newsletter_subscription, marketing_banner
