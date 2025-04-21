from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Quiz])
def read_quizzes(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    content_type: Optional[str] = None,
    content_id: Optional[str] = None,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve quizzes.
    """
    if content_type and content_id:
        quiz = crud.quiz.get_by_content(db, content_type=content_type, content_id=content_id)
        return [quiz] if quiz else []
    
    quizzes = crud.quiz.get_multi(db, skip=skip, limit=limit)
    return quizzes


@router.post("/", response_model=schemas.Quiz)
def create_quiz(
    *,
    db: Session = Depends(deps.get_db),
    quiz_in: schemas.QuizCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new quiz.
    """
    # Check if a quiz already exists for this content
    existing_quiz = crud.quiz.get_by_content(
        db, content_type=quiz_in.content_type, content_id=quiz_in.content_id
    )
    if existing_quiz:
        raise HTTPException(
            status_code=400,
            detail=f"Quiz already exists for this {quiz_in.content_type}",
        )
    
    quiz = crud.quiz.create_with_questions(db, obj_in=quiz_in)
    return quiz


@router.get("/{quiz_id}", response_model=schemas.Quiz)
def read_quiz(
    *,
    db: Session = Depends(deps.get_db),
    quiz_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get quiz by ID.
    """
    quiz = crud.quiz.get(db, id=quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz


@router.put("/{quiz_id}", response_model=schemas.Quiz)
def update_quiz(
    *,
    db: Session = Depends(deps.get_db),
    quiz_id: str,
    quiz_in: schemas.QuizUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a quiz.
    """
    quiz = crud.quiz.get(db, id=quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    quiz = crud.quiz.update(db, db_obj=quiz, obj_in=quiz_in)
    return quiz


@router.delete("/{quiz_id}", response_model=schemas.Quiz)
def delete_quiz(
    *,
    db: Session = Depends(deps.get_db),
    quiz_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a quiz.
    """
    quiz = crud.quiz.get(db, id=quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    quiz = crud.quiz.remove(db, id=quiz_id)
    return quiz


@router.post("/{quiz_id}/questions", response_model=schemas.QuizQuestion)
def create_quiz_question(
    *,
    db: Session = Depends(deps.get_db),
    quiz_id: str,
    question_in: schemas.QuizQuestionCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Add a question to a quiz.
    """
    quiz = crud.quiz.get(db, id=quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    question = crud.quiz.create_question(db, quiz_id=quiz_id, obj_in=question_in)
    db.commit()
    db.refresh(question)
    return question


@router.put("/questions/{question_id}", response_model=schemas.QuizQuestion)
def update_quiz_question(
    *,
    db: Session = Depends(deps.get_db),
    question_id: str,
    question_in: schemas.QuizQuestionUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a quiz question.
    """
    question = db.query(models.QuizQuestion).filter(models.QuizQuestion.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    question = crud.quiz.update_question(db, db_obj=question, obj_in=question_in)
    return question


@router.delete("/questions/{question_id}", response_model=schemas.QuizQuestion)
def delete_quiz_question(
    *,
    db: Session = Depends(deps.get_db),
    question_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a quiz question.
    """
    question = db.query(models.QuizQuestion).filter(models.QuizQuestion.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    question = crud.quiz.delete_question(db, id=question_id)
    return question


@router.post("/{quiz_id}/attempts", response_model=schemas.UserQuizAttempt)
def create_quiz_attempt(
    *,
    db: Session = Depends(deps.get_db),
    quiz_id: str,
    attempt_in: schemas.UserQuizAttemptCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Submit a quiz attempt.
    """
    quiz = crud.quiz.get(db, id=quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Ensure the quiz_id in the path matches the one in the request body
    if attempt_in.quiz_id != quiz_id:
        attempt_in.quiz_id = quiz_id
    
    # Create the attempt
    attempt = crud.user_quiz_attempt.create_with_user(
        db, obj_in=attempt_in, user_id=current_user.id
    )
    
    # Update user's experience and points based on quiz performance
    if attempt.passed:
        # Award experience points based on quiz score
        experience_gained = int(quiz.passing_score * (attempt.score / 100))
        current_user.experience += experience_gained
        
        # Award points
        points_gained = int(experience_gained * 0.5)  # Half of experience as points
        current_user.total_points += points_gained
        
        # Check if user leveled up (simple level calculation)
        new_level = 1 + (current_user.experience // 100)  # Level up every 100 XP
        if new_level > current_user.level:
            current_user.level = new_level
        
        db.add(current_user)
        db.commit()
    
    return attempt


@router.get("/{quiz_id}/attempts", response_model=List[schemas.UserQuizAttempt])
def read_quiz_attempts(
    *,
    db: Session = Depends(deps.get_db),
    quiz_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get all attempts for a quiz by the current user.
    """
    quiz = crud.quiz.get(db, id=quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    attempts = crud.user_quiz_attempt.get_by_user_and_quiz(
        db, user_id=current_user.id, quiz_id=quiz_id
    )
    return attempts


@router.get("/{quiz_id}/attempts/best", response_model=schemas.UserQuizAttempt)
def read_best_quiz_attempt(
    *,
    db: Session = Depends(deps.get_db),
    quiz_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get the best attempt for a quiz by the current user.
    """
    quiz = crud.quiz.get(db, id=quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    attempt = crud.user_quiz_attempt.get_best_by_user_and_quiz(
        db, user_id=current_user.id, quiz_id=quiz_id
    )
    if not attempt:
        raise HTTPException(status_code=404, detail="No attempts found for this quiz")
    
    return attempt
