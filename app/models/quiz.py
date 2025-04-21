from sqlalchemy import Boolean, Column, Integer, String, Text, ForeignKey, DateTime, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)

    # Quiz can be associated with different content types
    content_type = Column(String, nullable=False)  # 'post', 'series_article', 'booklet_chapter', etc.
    content_id = Column(String, nullable=False)

    # Quiz settings
    passing_score = Column(Float, default=70.0)  # Percentage needed to pass
    time_limit = Column(Integer, nullable=True)  # Time limit in seconds, null means no limit
    randomize_questions = Column(Boolean, default=False)
    show_correct_answers = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    questions = relationship("QuizQuestion", back_populates="quiz", cascade="all, delete-orphan")
    attempts = relationship("UserQuizAttempt", back_populates="quiz", cascade="all, delete-orphan")


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id = Column(String, primary_key=True, index=True)
    quiz_id = Column(String, ForeignKey("quizzes.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String, nullable=False)  # 'multiple_choice', 'true_false', 'short_answer'
    points = Column(Integer, default=1)
    explanation = Column(Text)  # Explanation shown after answering
    order = Column(Integer, default=0)  # For ordering questions

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    quiz = relationship("Quiz", back_populates="questions")
    answers = relationship("QuizAnswer", back_populates="question", cascade="all, delete-orphan")


class QuizAnswer(Base):
    __tablename__ = "quiz_answers"

    id = Column(String, primary_key=True, index=True)
    question_id = Column(String, ForeignKey("quiz_questions.id"), nullable=False)
    answer_text = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False)
    explanation = Column(Text)  # Explanation for this specific answer
    order = Column(Integer, default=0)  # For ordering answers

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    question = relationship("QuizQuestion", back_populates="answers")


class UserQuizAttempt(Base):
    __tablename__ = "user_quiz_attempts"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    quiz_id = Column(String, ForeignKey("quizzes.id"), nullable=False)
    score = Column(Float, nullable=False)  # Percentage score
    passed = Column(Boolean, default=False)
    time_taken = Column(Integer)  # Time taken in seconds
    answers = Column(JSON)  # Store user's answers as JSON

    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))

    # Relationships
    user = relationship("User", back_populates="quiz_attempts")
    quiz = relationship("Quiz", back_populates="attempts")
