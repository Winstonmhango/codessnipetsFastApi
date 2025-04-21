from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field


# Quiz Answer Schemas
class QuizAnswerBase(BaseModel):
    answer_text: str
    is_correct: bool = False
    explanation: Optional[str] = None
    order: int = 0


class QuizAnswerCreate(QuizAnswerBase):
    pass


class QuizAnswerUpdate(QuizAnswerBase):
    answer_text: Optional[str] = None
    is_correct: Optional[bool] = None


class QuizAnswer(QuizAnswerBase):
    id: str
    question_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Quiz Question Schemas
class QuizQuestionBase(BaseModel):
    question_text: str
    question_type: str  # 'multiple_choice', 'true_false', 'short_answer'
    points: int = 1
    explanation: Optional[str] = None
    order: int = 0


class QuizQuestionCreate(QuizQuestionBase):
    answers: List[QuizAnswerCreate]


class QuizQuestionUpdate(QuizQuestionBase):
    question_text: Optional[str] = None
    question_type: Optional[str] = None
    points: Optional[int] = None
    answers: Optional[List[Union[QuizAnswerCreate, QuizAnswerUpdate]]] = None


class QuizQuestion(QuizQuestionBase):
    id: str
    quiz_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    answers: List[QuizAnswer] = []

    class Config:
        from_attributes = True


# Quiz Schemas
class QuizBase(BaseModel):
    title: str
    description: Optional[str] = None
    content_type: str  # 'post', 'series_article', 'booklet_chapter', etc.
    content_id: str
    passing_score: float = 70.0
    time_limit: Optional[int] = None
    randomize_questions: bool = False
    show_correct_answers: bool = True


class QuizCreate(QuizBase):
    questions: Optional[List[QuizQuestionCreate]] = []


class QuizUpdate(QuizBase):
    title: Optional[str] = None
    description: Optional[str] = None
    content_type: Optional[str] = None
    content_id: Optional[str] = None
    passing_score: Optional[float] = None
    time_limit: Optional[int] = None
    randomize_questions: Optional[bool] = None
    show_correct_answers: Optional[bool] = None
    questions: Optional[List[Union[QuizQuestionCreate, QuizQuestionUpdate]]] = None


class Quiz(QuizBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    questions: List[QuizQuestion] = []

    class Config:
        from_attributes = True


# User Quiz Attempt Schemas
class UserQuizAttemptBase(BaseModel):
    quiz_id: str
    score: float
    passed: bool = False
    time_taken: Optional[int] = None
    answers: Dict[str, Any] = {}  # JSON object with question_id -> answer_id mapping


class UserQuizAttemptCreate(UserQuizAttemptBase):
    pass


class UserQuizAttemptUpdate(UserQuizAttemptBase):
    quiz_id: Optional[str] = None
    score: Optional[float] = None
    passed: Optional[bool] = None
    time_taken: Optional[int] = None
    answers: Optional[Dict[str, Any]] = None
    completed_at: Optional[datetime] = None


class UserQuizAttempt(UserQuizAttemptBase):
    id: str
    user_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Quiz with User Attempt
class QuizWithUserAttempt(Quiz):
    user_attempts: List[UserQuizAttempt] = []

    class Config:
        from_attributes = True
